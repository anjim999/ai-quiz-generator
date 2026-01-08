"""
Fallback Quiz Generator
=======================
Provides a fallback quiz when LLM is unavailable or quota exceeded.
"""

from typing import List, Dict, Any


def fallback_quiz(
    url: str,
    title: str,
    article_text: str,
    sections: List[str]
) -> Dict[str, Any]:
    """
    Generate a fallback quiz when LLM is unavailable.
    
    Args:
        url: Wikipedia article URL
        title: Article title
        article_text: Scraped article text
        sections: Article section headings
        
    Returns:
        Quiz payload following the standard format
    """
    
    base_options = ["Yes", "No", "Not stated", "Irrelevant"]
    
    quiz = []
    for i in range(5):
        quiz.append({
            "question": f"Is this article about '{title}'?",
            "options": base_options,
            "answer": "Yes",
            "difficulty": "easy",
            "explanation": "Fallback quiz - Gemini API quota was exceeded or key is missing."
        })
    
    return {
        "url": url,
        "title": title,
        "summary": f"Placeholder summary for {title}. Configure GEMINI_API_KEY for real AI-generated content.",
        "key_entities": {
            "people": [],
            "organizations": [],
            "locations": []
        },
        "sections": sections[:8] if sections else [],
        "quiz": quiz,
        "related_topics": ["Wikipedia", "Article", "Reference"]
    }
