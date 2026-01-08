"""
LLM Quiz Generator Service
==========================
Generates quizzes using LangChain with Google Gemini.

Assignment Requirements:
- LLM: Gemini or any free tier API via LangChain
- Include the LangChain prompt templates used

This module uses:
- LangChain for LLM orchestration
- Google Gemini (gemini-2.0-flash) as the LLM
- Custom prompt templates (see prompts/quiz_generation.py)
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional

from src.core import settings
from src.services.fallback import fallback_quiz

logger = logging.getLogger(__name__)

# Import prompt templates
import sys
sys.path.insert(0, str(__file__).replace('/app/services/llm_quiz_generator.py', ''))
from prompts.quiz_generation import (
    quiz_generation_prompt,
    supplementary_questions_prompt
)

# LangChain imports - will be initialized lazily
_llm = None


def get_llm():
    """
    Get or create the LangChain LLM instance.
    Uses lazy initialization to avoid import errors when API key is missing.
    Tries gemini-2.5-flash first, falls back to gemini-2.5-flash-lite.
    """
    global _llm
    
    if _llm is not None:
        return _llm
    
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured")
        return None
    
    # Models to try in order (primary, then fallback)
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
    
    for model_name in models_to_try:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            _llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.7,
                max_retries=2,
                timeout=60
            )
            #https://en.wikipedia.org/wiki/Artificial_intelligence
            logger.info(f"LangChain Gemini LLM initialized successfully with model: {model_name}")
            return _llm
            
        except Exception as e:
            logger.warning(f"Failed to initialize model {model_name}: {e}")
            continue
    
    logger.error("Failed to initialize any Gemini model")
    return None


def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON from LLM response text.
    Handles markdown code blocks and malformed JSON.
    
    Args:
        text: Raw LLM response text
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted
    """
    if not isinstance(text, str):
        raise ValueError("LLM returned non-string output")
    
    # Replace smart quotes
    t = text.replace('"', '"').replace('"', '"').replace("'", "'").replace("'", "'")
    
    # Remove markdown code blocks
    if "```json" in t:
        t = t.split("```json")[1].split("```")[0]
    elif "```" in t:
        t = t.split("```")[1].split("```")[0]
    
    # Find the first { and matching }
    first_brace = t.find("{")
    if first_brace == -1:
        raise ValueError("LLM returned unexpected format (no JSON object found)")
    
    # Find matching closing brace
    stack = 0
    end_index = -1
    
    for i in range(first_brace, len(t)):
        if t[i] == "{":
            stack += 1
        elif t[i] == "}":
            stack -= 1
            if stack == 0:
                end_index = i
                break
    
    if end_index == -1:
        # Try regex fallback
        import re
        match = re.search(r'\{[\s\S]*\}', t)
        if not match:
            raise ValueError("LLM returned unexpected format (no closing brace)")
        t = match.group(0)
    else:
        t = t[first_brace:end_index + 1]
    
    # Remove trailing commas
    t = t.replace(",\n}", "\n}").replace(",\n]", "\n]")
    t = t.replace(", }", " }").replace(", ]", " ]")
    
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        # Try cleaning control characters
        import re
        cleaned = re.sub(r'[\x00-\x1f]+', '', t)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw text: {text[:1000]}")
            raise ValueError("LLM returned invalid JSON")


async def generate_with_retry(
    chain,
    inputs: Dict[str, Any],
    max_retries: int = 3
) -> str:
    """
    Generate content with exponential backoff retry.
    
    Args:
        chain: LangChain chain or LLM
        inputs: Input variables for the chain
        max_retries: Maximum number of retry attempts
        
    Returns:
        Generated text content
    """
    delay = 2.0
    
    for attempt in range(1, max_retries + 1):
        try:
            # Run the chain
            result = await asyncio.to_thread(chain.invoke, inputs)
            
            # Handle different response types
            if hasattr(result, 'content'):
                return result.content
            elif isinstance(result, str):
                return result
            else:
                return str(result)
                
        except Exception as e:
            error_msg = str(e)
            
            # Check for retryable errors (503, 429)
            if "503" in error_msg or "429" in error_msg or "overloaded" in error_msg.lower():
                if attempt < max_retries:
                    logger.warning(f"LLM overloaded (attempt {attempt}/{max_retries}), retrying in {delay}s")
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
            
            # Non-retryable error or max retries reached
            raise


async def generate_quiz_payload(
    url: str,
    title: str,
    article_text: str,
    sections: List[str],
    count: int = 10
) -> Dict[str, Any]:
    """
    Generate a quiz payload using LangChain and Gemini.
    
    Args:
        url: Wikipedia article URL
        title: Article title
        article_text: Scraped article text
        sections: Article section headings
        count: Number of questions to generate
        
    Returns:
        Quiz payload following the standard format
    """
    
    llm = get_llm()
    
    if llm is None:
        logger.warning("LLM not available, using fallback quiz")
        return fallback_quiz(url, title, article_text, sections)
    
    try:
        # Create the chain: prompt | llm
        chain = quiz_generation_prompt | llm
        
        # Truncate article text if too long (Gemini has token limits)
        max_chars = 30000
        truncated_text = article_text[:max_chars]
        if len(article_text) > max_chars:
            truncated_text += "\n\n[Article truncated for processing...]"
        
        # Generate initial quiz
        logger.info(f"Generating quiz with {count} questions...")
        
        response_text = await generate_with_retry(
            chain,
            {
                "url": url,
                "title": title,
                "article_text": truncated_text,
                "count": count
            }
        )
        
        parsed = extract_json(response_text)
        
        # Extract and validate quiz questions
        quiz = []
        for q in parsed.get("quiz", []):
            if not q.get("question") or not q.get("options") or not q.get("answer"):
                continue
            
            quiz.append({
                "question": q["question"],
                "options": q.get("options", [])[:4],
                "answer": q["answer"],
                "difficulty": q.get("difficulty", "medium"),
                "explanation": q.get("explanation", "")
            })
        
        # If we didn't get enough questions, try to generate more
        attempts = 0
        max_attempts = 3
        
        while len(quiz) < count and attempts < max_attempts:
            attempts += 1
            remaining = count - len(quiz)
            
            logger.info(f"Need {remaining} more questions, attempt {attempts}")
            
            # Create previous questions summary
            prev_questions = "\n".join([
                f"- {i+1}. {q['question']}" 
                for i, q in enumerate(quiz)
            ]) or "None"
            
            # Generate more questions
            supp_chain = supplementary_questions_prompt | llm
            
            try:
                more_text = await generate_with_retry(
                    supp_chain,
                    {
                        "url": url,
                        "title": title,
                        "article_text": truncated_text,
                        "remaining": remaining,
                        "previous_questions": prev_questions
                    }
                )
                
                more_parsed = extract_json(more_text)
                
                # Add unique questions
                seen = set(q["question"] for q in quiz)
                for q in more_parsed.get("quiz", []):
                    if q.get("question") and q["question"] not in seen:
                        quiz.append({
                            "question": q["question"],
                            "options": q.get("options", [])[:4],
                            "answer": q.get("answer", ""),
                            "difficulty": q.get("difficulty", "medium"),
                            "explanation": q.get("explanation", "")
                        })
                        seen.add(q["question"])
                    
                    if len(quiz) >= count:
                        break
                        
            except Exception as e:
                logger.warning(f"Failed to generate supplementary questions: {e}")
                break
        
        # Trim to requested count
        quiz = quiz[:count]
        
        logger.info(f"Generated {len(quiz)} quiz questions successfully")
        
        return {
            "url": url,
            "title": title,
            "summary": parsed.get("summary", ""),
            "key_entities": parsed.get("key_entities", {
                "people": [],
                "organizations": [],
                "locations": []
            }),
            "sections": parsed.get("sections", sections),
            "quiz": quiz,
            "related_topics": parsed.get("related_topics", [])
        }
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        logger.exception("Full traceback:")
        return fallback_quiz(url, title, article_text, sections)
