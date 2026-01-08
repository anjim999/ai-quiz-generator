// src/pages/ResultPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authHeaders } from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  FaDownload,
  FaRedo,
  FaTimes,
  FaTrophy,
  FaClock,
  FaCheckCircle,
  FaTimesCircle
} from "react-icons/fa";

export default function ResultPage() {
  const nav = useNavigate();
  const { auth } = useAuth();
  const [result, setResult] = useState(null);

  useEffect(() => {
    const data = JSON.parse(localStorage.getItem("lastResult"));
    if (!data) return nav("/dashboard");
    setResult(data);
  }, []);

  if (!result) return null;

  const mins = Math.floor(result.usedTime / 60);
  const secs = result.usedTime % 60;
  const percentage = Math.round((result.score / result.count) * 100);

  // Determine performance level
  const getPerformance = () => {
    if (percentage >= 80) return {
      label: "Excellent",
      class: "score-excellent",
      color: "text-emerald-600",
      message: "Outstanding performance! You've mastered this topic."
    };
    if (percentage >= 60) return {
      label: "Good",
      class: "score-good",
      color: "text-indigo-600",
      message: "Good job! You have a solid understanding of the material."
    };
    if (percentage >= 40) return {
      label: "Average",
      class: "score-average",
      color: "text-amber-600",
      message: "You're on the right track. Review the material for better results."
    };
    return {
      label: "Needs Improvement",
      class: "score-poor",
      color: "text-red-600",
      message: "Consider reviewing the topic and trying again."
    };
  };

  const performance = getPerformance();

  const retakeQuiz = () => {
    let active = JSON.parse(localStorage.getItem("activeQuiz"));
    if (active) {
      active.answers = {};
      localStorage.setItem("activeQuiz", JSON.stringify(active));
    }
    nav("/exam");
  };

  const downloadPDF = async () => {
    try {
      const headers = authHeaders({ "Content-Type": "application/json" });
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/api/quiz/export_pdf/${result.quizId}`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({
            user: auth?.user?.name || auth?.user?.email || "Anonymous",
            count: result.count,
            duration_str: `${mins}m ${secs}s`,
            user_answers: result.answers,
            score: result.score,
            total: result.count,
          }),
        }
      );

      if (res.status === 401) {
        alert("Please log in to download the PDF.");
        return;
      }

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        alert(`Failed to download PDF: ${res.status}`);
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `quiz_result_${result.quizId}.pdf`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      console.error("Failed to download PDF", err);
      alert("Failed to download PDF");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="card max-w-lg w-full animate-fade-in">
        {/* Header */}
        <div className="card-header text-center py-6">
          <FaTrophy className={`w-10 h-10 mx-auto mb-2 ${performance.color}`} />
          <h1 className="text-heading text-slate-900">Exam Completed</h1>
        </div>

        <div className="card-body">
          {/* Score Circle */}
          <div className="flex justify-center mb-8">
            <div className={`score-circle ${performance.class}`}>
              <div className="text-center">
                <div className="text-3xl font-bold">{percentage}%</div>
                <div className="text-xs font-medium opacity-75">{performance.label}</div>
              </div>
            </div>
          </div>

          {/* Performance Message */}
          <p className="text-center text-slate-600 mb-6">
            {performance.message}
          </p>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="text-center p-4 rounded-lg bg-slate-50">
              <FaCheckCircle className="w-5 h-5 mx-auto mb-2 text-emerald-500" />
              <div className="text-xl font-bold text-slate-900">{result.score}</div>
              <div className="text-xs text-slate-500">Correct</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-slate-50">
              <FaTimesCircle className="w-5 h-5 mx-auto mb-2 text-red-500" />
              <div className="text-xl font-bold text-slate-900">{result.count - result.score}</div>
              <div className="text-xs text-slate-500">Incorrect</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-slate-50">
              <FaClock className="w-5 h-5 mx-auto mb-2 text-indigo-500" />
              <div className="text-xl font-bold text-slate-900">{mins}:{String(secs).padStart(2, '0')}</div>
              <div className="text-xs text-slate-500">Time Taken</div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="space-y-2 text-sm border-t border-slate-100 pt-4 mb-6">
            <div className="flex justify-between text-slate-600">
              <span>Total Questions</span>
              <span className="font-medium text-slate-900">{result.count}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Allowed Time</span>
              <span className="font-medium text-slate-900">{result.count} minutes</span>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-3">
            <button
              className="btn btn-primary w-full"
              onClick={downloadPDF}
            >
              <FaDownload className="w-4 h-4" />
              Download PDF Report
            </button>

            <div className="grid grid-cols-2 gap-3">
              <button
                className="btn btn-secondary"
                onClick={retakeQuiz}
              >
                <FaRedo className="w-4 h-4" />
                Retake
              </button>

              <button
                className="btn btn-ghost"
                onClick={() => nav("/dashboard")}
              >
                <FaTimes className="w-4 h-4" />
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
