# AI Quiz Generator (FAST APIs)

A modern, full-stack application that generates interactive quizzes from any Wikipedia article using Google's Gemini AI. 

![AI Quiz Generator Preview](/home/anji/.gemini/antigravity/brain/a64e1c68-dba3-4618-838b-31d43a74f436/uploaded_image_1767972017572.png)

## 🚀 Features

- **AI-Powered Generation**: Instantly creates 5-10 question quizzes from Wikipedia URLs.
- **Interactive Quiz Mode**: Real-time scoring, immediate feedback, and detailed explanations.
- **History & Tracking**: Save your quiz results and review past attempts.
- **PDF Export**: Download quizzes as professionally formatted PDFs for offline use.
- **Modern UI**: Clean, responsive interface built with React, TailwindCSS, and Glassmorphism design.
- **Secure Authentication**: User accounts with JWT support and Google OAuth.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 (Vite)
- **Styling**: TailwindCSS v4
- **State Management**: React Context
- **Routing**: React Router v7
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (AsyncPG)
- **AI Model**: Google Gemini Pro (via LangChain)
- **Scraping**: BeautifulSoup4
- **PDF Engine**: ReportLab

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v18+)
- **Python** (v3.11+)
- **PostgreSQL** (v13+)
- **Google Gemini API Key** (Get one [here](https://aistudio.google.com/app/apikey))

## 🏁 Getting Started

### 1. Backend Setup

The backend handles AI generation, database operations, and authentication.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the `backend` directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/quiz_db
   JWT_SECRET=your_super_secret_key_here
   GEMINI_API_KEY=your_google_gemini_api_key
   CORS_ORIGINS=http://localhost:5173
   ```
   *(Make sure to update the database credentials)*

5. **Start the Backend Server:**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```
   The API will be available at `http://localhost:8000`.

### 2. Frontend Setup

The frontend provides the user interface for generating and taking quizzes.

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   The app will run at `http://localhost:5173`.

## 🧪 Testing

### Backend Testing
You can run the backend tests (if configured) or test endpoints manually via the interactive documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Frontend Testing
Open the application in your browser and try the following flow:
1. Register a new user account.
2. Go to "Generate Quiz" and paste a Wikipedia URL (e.g., `https://en.wikipedia.org/wiki/Python_(programming_language)`).
3. Wait for the AI to generate the quiz.
4. Take the quiz and submit your answers.
5. Check your history in the dashboard.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.
