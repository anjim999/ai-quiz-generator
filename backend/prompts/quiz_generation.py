"""
LangChain Prompt Templates
==========================
Prompt templates for quiz generation using LangChain.

These templates are designed for optimal quiz generation with:
- Clear instructions for the LLM
- Structured output format
- Grounding in article content to minimize hallucination
- Difficulty level distribution

EVALUATION CRITERIA (from assignment):
- Effectiveness and clarity of prompts
- Grounding of outputs in article content
- Minimization of hallucination
"""

from langchain.prompts import PromptTemplate


# ===========================================
# Quiz Generation Prompt Template
# ===========================================

QUIZ_GENERATION_TEMPLATE = """You are an expert quiz generator specializing in educational content.
Your task is to generate a high-quality quiz based on the provided Wikipedia article.

ARTICLE INFORMATION:
-------------------
URL: {url}
Title: {title}

ARTICLE CONTENT:
----------------
{article_text}

TASK:
-----
Generate exactly {count} multiple-choice questions based ONLY on the information provided in the article above.

REQUIREMENTS:
1. Each question must be directly answerable from the article content
2. Questions should cover different sections/topics from the article
3. Difficulty distribution: approximately 30% easy, 50% medium, 20% hard
4. Each question must have exactly 4 options (A-D)
5. Only ONE option should be correct
6. Wrong options should be plausible but clearly incorrect based on the article
7. Explanations should reference specific parts of the article

OUTPUT FORMAT (strict JSON):
{{
    "url": "{url}",
    "title": "{title}",
    "summary": "A 2-3 sentence summary of the article's main topic",
    "key_entities": {{
        "people": ["List of important people mentioned"],
        "organizations": ["List of organizations mentioned"],
        "locations": ["List of locations mentioned"]
    }},
    "sections": ["List of main section headings from the article"],
    "quiz": [
        {{
            "question": "Clear, specific question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "The correct option (must match one of the options exactly)",
            "difficulty": "easy|medium|hard",
            "explanation": "Brief explanation referencing the article section"
        }}
    ],
    "related_topics": ["5-8 related Wikipedia topics for further reading"]
}}

CRITICAL RULES:
- Output ONLY valid JSON, no markdown code blocks
- Do NOT hallucinate or add information not in the article
- Questions must be educational and factually accurate
- Each answer must be verifiable from the article text
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["url", "title", "article_text", "count"],
    template=QUIZ_GENERATION_TEMPLATE
)


# ===========================================
# Supplementary Questions Template
# ===========================================
# Used when we need more questions to reach the target count

SUPPLEMENTARY_QUESTIONS_TEMPLATE = """You are an expert quiz generator.
Generate {remaining} MORE unique questions from this article.

ARTICLE:
URL: {url}
Title: {title}

CONTENT:
{article_text}

PREVIOUSLY GENERATED QUESTIONS (do NOT repeat these):
{previous_questions}

Generate {remaining} NEW questions that:
1. Cover different aspects of the article
2. Do NOT duplicate any previous questions
3. Follow the same format as before

OUTPUT FORMAT (strict JSON):
{{
    "quiz": [
        {{
            "question": "New question text",
            "options": ["A", "B", "C", "D"],
            "answer": "Correct answer",
            "difficulty": "easy|medium|hard",
            "explanation": "Brief explanation"
        }}
    ]
}}

Output ONLY valid JSON, no markdown.
"""

supplementary_questions_prompt = PromptTemplate(
    input_variables=["url", "title", "article_text", "remaining", "previous_questions"],
    template=SUPPLEMENTARY_QUESTIONS_TEMPLATE
)


# ===========================================
# Related Topics Template
# ===========================================
# For generating related Wikipedia topics

RELATED_TOPICS_TEMPLATE = """Based on the following Wikipedia article, suggest 5-8 related topics
that would be good for further reading.

Article Title: {title}
Article Summary: {summary}
Main Topics Covered: {sections}

Suggest related Wikipedia topics that:
1. Are directly related to the main subject
2. Would help readers understand the topic better
3. Cover related historical, scientific, or cultural aspects
4. Are actual Wikipedia article titles

Output as a JSON array of strings:
["Topic 1", "Topic 2", "Topic 3", ...]

Output ONLY the JSON array, nothing else.
"""

related_topics_prompt = PromptTemplate(
    input_variables=["title", "summary", "sections"],
    template=RELATED_TOPICS_TEMPLATE
)


# ===========================================
# Prompt Template Documentation (for README)
# ===========================================

PROMPT_DOCUMENTATION = """
# LangChain Prompt Templates Documentation

## 1. Quiz Generation Prompt (`quiz_generation_prompt`)

### Purpose
Generates the main quiz with questions, answers, and metadata from a Wikipedia article.

### Input Variables
- `url`: Wikipedia article URL
- `title`: Article title
- `article_text`: Scraped article content
- `count`: Number of questions to generate

### Output
JSON object containing:
- Article summary
- Key entities (people, organizations, locations)
- Section list
- Quiz questions with options, answers, difficulty, and explanations
- Related topics for further reading

### Design Decisions
1. **Grounding**: The prompt explicitly states to generate questions ONLY from the provided content
2. **Difficulty Distribution**: Specifies 30% easy, 50% medium, 20% hard
3. **Anti-Hallucination**: Multiple reminders to not add external information
4. **Structured Output**: Detailed JSON schema prevents format errors

## 2. Supplementary Questions Prompt (`supplementary_questions_prompt`)

### Purpose
Generates additional questions when the initial generation didn't produce enough.

### Design Decisions
1. **Deduplication**: Includes previously generated questions to avoid repeats
2. **Focused Output**: Only generates quiz questions, not full metadata

## 3. Related Topics Prompt (`related_topics_prompt`)

### Purpose
Suggests related Wikipedia topics for further reading.

### Design Decisions
1. **Context-Aware**: Uses title, summary, and sections for context
2. **Validation Hint**: Asks for actual Wikipedia article titles
"""


def get_prompt_documentation() -> str:
    """Return the prompt template documentation for README."""
    return PROMPT_DOCUMENTATION
