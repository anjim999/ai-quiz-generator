# AI Quiz Generator - FastAPI Backend

A production-grade FastAPI backend for generating quizzes from Wikipedia articles using LangChain and Google Gemini AI.

**Built for DeepKlarity Technologies Assignment**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-purple.svg)

## 🚀 Features

### Core Features
- ✅ **Quiz Generation** - Generate 5-10 AI-powered questions from any Wikipedia article
- ✅ **Take Quiz Mode** - Submit answers and get scored with explanations
- ✅ **History View** - Browse previously generated quizzes
- ✅ **PDF Export** - Export quizzes as professionally formatted PDFs
- ✅ **User Authentication** - JWT-based auth with Google OAuth support

### Bonus Features
- ✅ **URL Caching** - Prevents duplicate scraping of the same URL
- ✅ **Raw HTML Storage** - Stores scraped HTML in database for reference
- ✅ **URL Validation** - Validates Wikipedia URLs before processing
- ✅ **User Scoring** - Tracks scores for quiz attempts
- ✅ **Section Extraction** - Extracts article sections for display

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL |
| **LLM** | Google Gemini via LangChain |
| **Web Scraping** | BeautifulSoup4 |
| **Authentication** | JWT + Google OAuth |
| **PDF Generation** | ReportLab |
| **HTTP Client** | httpx (async) |
| **Validation** | Pydantic v2 |

## 📁 Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   │
│   ├── core/                      # Core configurations
│   │   ├── __init__.py            # Pydantic Settings
│   │   ├── security.py            # JWT, password hashing
│   │   └── exceptions.py          # Custom exceptions
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── database.py            # Async PostgreSQL pool
│   │   ├── init.py                # Schema initialization
│   │   └── queries/               # SQL query functions
│   │       ├── users.py
│   │       ├── quizzes.py
│   │       └── otps.py
│   │
│   ├── models/                    # Pydantic models
│   │   ├── auth.py                # Auth request/response models
│   │   ├── quiz.py                # Quiz models
│   │   └── user.py                # User models
│   │
│   ├── routers/                   # API routes
│   │   ├── auth.py                # Auth endpoints
│   │   ├── quiz.py                # Quiz endpoints
│   │   └── admin.py               # Admin endpoints
│   │
│   ├── services/                  # Business logic
│   │   ├── llm_quiz_generator.py  # LangChain + Gemini
│   │   ├── scraper.py             # BeautifulSoup scraping
│   │   ├── pdf_generator.py       # PDF export
│   │   └── fallback.py            # Fallback quiz
│   │
│   ├── middleware/                # Auth middleware
│   │   └── auth.py
│   │
│   └── utils/                     # Utilities
│       ├── helpers.py
│       ├── otp.py
│       └── mailer.py
│
├── prompts/                       # LangChain prompt templates
│   └── quiz_generation.py
│
├── sample_data/                   # Test data
│   ├── urls.txt
│   └── outputs/
│
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Google Gemini API key (free tier available)

### 1. Clone the Repository

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_db
JWT_SECRET=your-super-secret-jwt-key
GEMINI_API_KEY=your-gemini-api-key

# Optional
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:5173
GOOGLE_CLIENT_ID=your-google-client-id
BREVO_API_KEY=your-brevo-api-key
```

### 5. Create Database

```bash
createdb quiz_db
```

The tables will be created automatically on first run.

### 6. Run the Server

```bash
# Development mode with hot reload
uvicorn src.main:app --reload --port 8000

# Or run directly
python -m src.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register-request-otp` | Request registration OTP |
| POST | `/api/auth/register-verify` | Verify OTP and complete registration |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/forgot-password-request` | Request password reset OTP |
| POST | `/api/auth/forgot-password-verify` | Verify OTP and reset password |
| POST | `/api/auth/google` | Google OAuth login |

### Quiz

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quiz/health` | Health check |
| POST | `/api/quiz/generate_quiz` | Generate quiz from Wikipedia URL |
| GET | `/api/quiz/history` | Get user's quiz history |
| GET | `/api/quiz/quiz/{quiz_id}` | Get a specific quiz |
| POST | `/api/quiz/submit_attempt/{quiz_id}` | Submit quiz attempt |
| POST | `/api/quiz/export_pdf/{quiz_id}` | Export quiz as PDF |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | Get all users (admin only) |
| GET | `/api/admin/user/{user_id}/attempts` | Get user's attempts (admin only) |

## 📝 Sample API Output

```json
{
  "id": 1,
  "url": "https://en.wikipedia.org/wiki/Alan_Turing",
  "title": "Alan Turing",
  "summary": "Alan Turing was a British mathematician and computer scientist...",
  "key_entities": {
    "people": ["Alan Turing", "Alonzo Church"],
    "organizations": ["University of Cambridge", "Bletchley Park"],
    "locations": ["United Kingdom"]
  },
  "sections": ["Early life", "World War II", "Legacy"],
  "quiz": [
    {
      "question": "Where did Alan Turing study?",
      "options": [
        "Harvard University",
        "Cambridge University",
        "Oxford University",
        "Princeton University"
      ],
      "answer": "Cambridge University",
      "difficulty": "easy",
      "explanation": "Mentioned in the 'Early life' section."
    }
  ],
  "related_topics": ["Cryptography", "Enigma machine", "Computer science"]
}
```

## 🎯 LangChain Prompt Templates

The quiz generation uses carefully designed prompt templates located in `prompts/quiz_generation.py`.

### Quiz Generation Prompt

```python
QUIZ_GENERATION_TEMPLATE = """
You are an expert quiz generator specializing in educational content.
Your task is to generate a high-quality quiz based on the provided Wikipedia article.

ARTICLE INFORMATION:
URL: {url}
Title: {title}

ARTICLE CONTENT:
{article_text}

TASK:
Generate exactly {count} multiple-choice questions based ONLY on the article.

REQUIREMENTS:
1. Each question must be directly answerable from the article content
2. Difficulty distribution: 30% easy, 50% medium, 20% hard
3. Each question must have exactly 4 options
4. Wrong options should be plausible but clearly incorrect

OUTPUT FORMAT (strict JSON):
{
    "url": "...",
    "title": "...",
    "summary": "...",
    "key_entities": {...},
    "sections": [...],
    "quiz": [...],
    "related_topics": [...]
}

CRITICAL RULES:
- Output ONLY valid JSON
- Do NOT hallucinate or add information not in the article
"""
```

### Design Decisions

1. **Grounding**: Explicit instruction to use ONLY article content prevents hallucination
2. **Difficulty Distribution**: 30% easy, 50% medium, 20% hard for balanced quizzes
3. **Structured Output**: Detailed JSON schema prevents format errors
4. **Anti-Hallucination**: Multiple reminders to not add external information

## 🧪 Testing

### Sample URLs for Testing

See `sample_data/urls.txt` for tested URLs:
- https://en.wikipedia.org/wiki/Alan_Turing
- https://en.wikipedia.org/wiki/Artificial_intelligence
- https://en.wikipedia.org/wiki/Albert_Einstein
- https://en.wikipedia.org/wiki/Python_(programming_language)

### Sample Outputs

See `sample_data/outputs/` for example JSON responses.

## 🚀 Deployment

### Deploy on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=your-production-db-url
JWT_SECRET=your-production-secret
GEMINI_API_KEY=your-api-key
```

## 📊 Evaluation Criteria Addressed

| Criteria | Implementation |
|----------|---------------|
| **Prompt Design** | Detailed templates with anti-hallucination measures |
| **Quiz Quality** | Difficulty distribution, explanations, related topics |
| **Extraction Quality** | BeautifulSoup with clean text extraction |
| **Functionality** | Complete end-to-end flow |
| **Code Quality** | Modular, typed, documented |
| **Error Handling** | Custom exceptions, graceful fallbacks |
| **UI Design** | React frontend with tabs and modals |
| **Database Accuracy** | PostgreSQL with proper schema |
| **Testing Evidence** | Sample data and screenshots |

## 📄 License

This project was created for the DeepKlarity Technologies assignment.

## 👤 Author

Built with ❤️ for the AI Quiz Generator assignment.
