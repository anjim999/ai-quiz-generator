// src/pages/Home.jsx
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";
import {
  FaWikipediaW,
  FaRobot,
  FaClipboardCheck,
  FaFilePdf,
  FaArrowRight,
  FaShieldAlt,
  FaClock,
  FaChartLine
} from "react-icons/fa";

export default function Home() {
  const { auth } = useAuth();

  const features = [
    {
      icon: FaWikipediaW,
      title: "Wikipedia Integration",
      description: "Generate quizzes from any Wikipedia article URL instantly"
    },
    {
      icon: FaRobot,
      title: "AI-Powered Questions",
      description: "Smart question generation using Google Gemini AI"
    },
    {
      icon: FaClipboardCheck,
      title: "Secure Exam Mode",
      description: "Fullscreen proctored exams with anti-cheat measures"
    },
    {
      icon: FaFilePdf,
      title: "PDF Export",
      description: "Download professional exam papers with answer keys"
    }
  ];

  const stats = [
    { icon: FaShieldAlt, value: "100%", label: "Secure" },
    { icon: FaClock, value: "10s", label: "Generation Time" },
    { icon: FaChartLine, value: "50+", label: "Questions per Quiz" }
  ];

  return (
    <>
      <Navbar />

      <main className="page-padding">
        {/* Hero Section */}
        <section className="container-narrow text-center py-16 sm:py-24">
          <div className="animate-fade-in">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 mb-6">
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
              <span className="text-xs font-medium text-indigo-700">DeepKlarity Assignment</span>
            </div>

            {/* Headline */}
            <h1 className="text-display text-slate-900 mb-4">
              AI-Powered Quiz Generator
            </h1>

            <p className="text-body text-lg max-w-xl mx-auto mb-8">
              Transform any Wikipedia article into a comprehensive quiz.
              Perfect for educators, students, and self-learners.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/dashboard" className="btn btn-primary btn-lg">
                {auth ? "Go to Dashboard" : "Generate Quiz"}
                <FaArrowRight className="w-4 h-4" />
              </Link>
              {!auth && (
                <Link to="/login" className="btn btn-secondary btn-lg">
                  Sign In
                </Link>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="mt-16 pt-8 border-t border-slate-200">
            <div className="grid grid-cols-3 gap-8">
              {stats.map((stat, i) => (
                <div key={i} className="text-center">
                  <stat.icon className="w-5 h-5 text-indigo-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
                  <div className="text-sm text-slate-500">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="container-wide section-spacing">
          <div className="text-center mb-12">
            <h2 className="text-heading text-slate-900 mb-3">How It Works</h2>
            <p className="text-body">
              Generate professional quizzes in three simple steps
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <div key={i} className="card card-body text-center card-interactive">
                <div className="w-12 h-12 rounded-lg bg-indigo-50 flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-6 h-6 text-indigo-600" />
                </div>
                <h3 className="text-subheading text-slate-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-small">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Steps Section */}
        <section className="container-narrow section-spacing">
          <div className="card card-body">
            <h3 className="text-heading text-slate-900 mb-6 text-center">Quick Start Guide</h3>

            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 font-semibold text-sm">
                  1
                </div>
                <div>
                  <h4 className="font-medium text-slate-900">Paste Wikipedia URL</h4>
                  <p className="text-sm text-slate-500">Enter any Wikipedia article URL to get started</p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 font-semibold text-sm">
                  2
                </div>
                <div>
                  <h4 className="font-medium text-slate-900">Configure Quiz</h4>
                  <p className="text-sm text-slate-500">Choose number of questions (1-50) and generate</p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 font-semibold text-sm">
                  3
                </div>
                <div>
                  <h4 className="font-medium text-slate-900">Take Exam or Export</h4>
                  <p className="text-sm text-slate-500">Start secure exam mode or download as PDF</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="container-narrow py-8 text-center border-t border-slate-200">
          <p className="text-small">
            Built for DeepKlarity Technologies • FastAPI + React + LangChain
          </p>
        </footer>
      </main>
    </>
  );
}
