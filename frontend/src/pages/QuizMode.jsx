// src/pages/QuizMode.jsx
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Timer from "../components/Timer";
import AntiTabSwitch from "../components/AntiTabSwitch";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { submitAttempt } from "../services/api";
import {
  FaExclamationTriangle,
  FaCheck,
  FaExpand,
  FaClock,
  FaShieldAlt
} from "react-icons/fa";

export default function QuizMode() {
  const nav = useNavigate();

  const active = useMemo(() => {
    const raw = localStorage.getItem("activeQuiz");
    return raw ? JSON.parse(raw) : null;
  }, []);

  const [submitted, setSubmitted] = useState(false);
  const [fsExitCount, setFsExitCount] = useState(0);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const [isFsModal, setIsFsModal] = useState(false);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const answersRef = useRef(answers);
  const startTimeRef = useRef(Date.now());
  const camRef = useRef(null);

  if (!active)
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="card card-body text-center max-w-md">
          <FaExclamationTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-heading text-slate-900 mb-2">No Active Quiz</h2>
          <p className="text-body mb-6">Please generate a quiz first from the dashboard.</p>
          <button onClick={() => nav("/dashboard")} className="btn btn-primary">
            Go to Dashboard
          </button>
        </div>
      </div>
    );

  const count = active.quiz.length;
  const totalSeconds = count * 60;
  const answeredCount = Object.keys(answers).length;
  const progress = (answeredCount / count) * 100;

  function scoreNow() {
    let s = 0;
    active.quiz.forEach((q, i) => {
      if (
        answersRef.current[i] !== undefined &&
        q.options[answersRef.current[i]] === q.answer
      )
        s++;
    });
    return s;
  }

  function stopCamera() {
    try {
      camRef.current?.getTracks().forEach((t) => t.stop());
    } catch { }
  }

  async function submitExam(auto = false) {
    if (submitted) return;
    setSubmitted(true);

    stopCamera();
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
    } catch { }

    const usedTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
    const score = scoreNow();

    // Convert answers from {index: optionIndex} to {index: answerText}
    const formattedAnswers = {};
    active.quiz.forEach((q, i) => {
      const selectedOptionIndex = answersRef.current[i];
      formattedAnswers[String(i)] = selectedOptionIndex !== undefined
        ? q.options[selectedOptionIndex]
        : "";
    });

    try {
      const res = await submitAttempt(active.id, {
        answers: formattedAnswers,
        score,
        time_taken_seconds: usedTime,
        total_time: totalSeconds,
        total_questions: count,
        auto_submitted: auto,
      });

      if (!res?.saved) {
        toast.error("Server did not confirm save");
      } else {
        toast.success(`Submitted! Score: ${score}/${count}`);
      }
    } catch (err) {
      console.error("Submit attempt failed:", err);
      toast.error("Server save failed");
    }

    setTimeout(() => {
      localStorage.setItem(
        "lastResult",
        JSON.stringify({
          quizId: active.id,
          score,
          usedTime,
          totalSeconds,
          count,
          answers: formattedAnswers, // Include user answers for PDF export
        })
      );
      nav("/result");
    }, 900);
  }

  function addStrike(type) {
    if (submitted) return;

    const newFs = type === "fs" ? fsExitCount + 1 : fsExitCount;
    const newTab = type === "tab" ? tabSwitchCount + 1 : tabSwitchCount;

    setFsExitCount(newFs);
    setTabSwitchCount(newTab);

    const total = newFs + newTab;
    toast.warn(`Security Violation ${total}/3`);

    if (newFs >= 3 || newTab >= 3 || (newFs >= 1 && newTab >= 1) || total >= 3) {
      toast.error("Maximum violations reached. Auto-submitting exam.");
      setTimeout(() => submitExam(true), 400);
    }
  }

  useEffect(() => {
    const start = async () => {
      try {
        if (!document.fullscreenElement)
          await document.documentElement.requestFullscreen();
      } catch { }

      try {
        const s = await navigator.mediaDevices.getUserMedia({ video: true });
        camRef.current = s;
      } catch {
        toast.error("Webcam access required");
        return submitExam(true);
      }
    };

    const keyBlock = (e) => {
      const k = e.key.toLowerCase();
      if (k === "f5" || (e.ctrlKey && k === "r")) {
        e.preventDefault();
        toast.warn("Page refresh is disabled during exam");
      }
      if (k === "f12" || (e.ctrlKey && e.shiftKey && ["i", "j", "c"].includes(k))) {
        e.preventDefault();
        toast.warn("Developer tools are disabled during exam");
      }
    };

    const noContext = (e) => e.preventDefault();

    document.addEventListener("keydown", keyBlock);
    window.addEventListener("contextmenu", noContext);

    start();

    return () => {
      document.removeEventListener("keydown", keyBlock);
      window.removeEventListener("contextmenu", noContext);
      stopCamera();
    };
  }, []);

  useEffect(() => {
    const handleFS = () => {
      if (!document.fullscreenElement && !submitted) {
        setIsFsModal(true);
        addStrike("fs");
      }
    };
    document.addEventListener("fullscreenchange", handleFS);
    return () => document.removeEventListener("fullscreenchange", handleFS);
  }, [submitted, fsExitCount, tabSwitchCount]);

  return (
    <div className="min-h-screen bg-slate-50">
      <ToastContainer position="top-center" />

      {/* Exam Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="container-wide py-4">
          <div className="flex items-center justify-between">
            {/* Left - Title & Info */}
            <div className="flex items-center gap-4">
              <div>
                <h1 className="font-semibold text-slate-900 text-lg truncate max-w-xs sm:max-w-md">
                  {active.title}
                </h1>
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span>{answeredCount}/{count} answered</span>
                  <span className="flex items-center gap-1">
                    <FaShieldAlt className={`w-3 h-3 ${fsExitCount + tabSwitchCount > 0 ? 'text-amber-500' : 'text-emerald-500'}`} />
                    Violations: {fsExitCount + tabSwitchCount}/3
                  </span>
                </div>
              </div>
            </div>

            {/* Right - Timer & Submit */}
            <div className="flex items-center gap-4">
              <Timer totalSeconds={totalSeconds} onEnd={() => submitExam(true)} />
              <button
                className="btn btn-primary"
                onClick={() => submitExam(false)}
                disabled={submitted}
              >
                <FaCheck className="w-3 h-3" />
                Submit
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-3">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      </header>

      <AntiTabSwitch onStrike={() => addStrike("tab")} maxStrikes={3} />

      {/* Questions */}
      <main className="container-narrow py-8">
        {/* Question Navigation */}
        <div className="flex flex-wrap gap-2 mb-6">
          {active.quiz.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentQuestion(i)}
              className={`
                w-10 h-10 rounded-lg text-sm font-medium cursor-pointer
                transition-all duration-200
                ${answers[i] !== undefined
                  ? 'bg-emerald-600 text-white'
                  : 'bg-white border border-slate-300 text-slate-600 hover:border-slate-400'
                }
                ${currentQuestion === i ? 'ring-2 ring-indigo-500 ring-offset-2' : ''}
              `}
            >
              {i + 1}
            </button>
          ))}
        </div>

        {/* Current Question Card */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <span className="badge badge-neutral">
                Question {currentQuestion + 1} of {count}
              </span>
              <span className={`badge ${active.quiz[currentQuestion].difficulty === 'easy' ? 'badge-success' :
                active.quiz[currentQuestion].difficulty === 'medium' ? 'badge-warning' : 'badge-danger'
                }`}>
                {active.quiz[currentQuestion].difficulty}
              </span>
            </div>
          </div>

          <div className="card-body">
            <p className="text-lg font-medium text-slate-900 mb-6">
              {active.quiz[currentQuestion].question}
            </p>

            <div className="space-y-3">
              {active.quiz[currentQuestion].options.map((opt, j) => (
                <label
                  key={j}
                  className={`option-label flex items-center gap-3 ${answers[currentQuestion] === j ? 'option-label-selected' : ''
                    }`}
                >
                  <input
                    type="radio"
                    name={`q${currentQuestion}`}
                    checked={answers[currentQuestion] === j}
                    onChange={() => {
                      const newAnswers = { ...answers, [currentQuestion]: j };
                      setAnswers(newAnswers);
                      answersRef.current = newAnswers;
                    }}
                    className="w-4 h-4 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-slate-700">{opt}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="card-footer flex justify-between">
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
            >
              Previous
            </button>

            {currentQuestion < count - 1 ? (
              <button
                className="btn btn-primary"
                onClick={() => setCurrentQuestion(currentQuestion + 1)}
              >
                Next
              </button>
            ) : (
              <button
                className="btn btn-success"
                onClick={() => submitExam(false)}
                disabled={submitted}
              >
                <FaCheck className="w-3 h-3" />
                Submit Exam
              </button>
            )}
          </div>
        </div>
      </main>

      {/* Fullscreen Modal */}
      {isFsModal && !submitted && (
        <div className="fixed inset-0 bg-slate-900/80 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-8 text-center animate-fade-in">
            <FaExpand className="w-12 h-12 text-amber-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-slate-900 mb-2">
              Fullscreen Required
            </h2>
            <p className="text-slate-600 mb-6">
              You have exited fullscreen mode. This has been recorded as a violation.
              Please return to fullscreen to continue your exam.
            </p>
            <button
              className="btn btn-primary btn-lg w-full cursor-pointer"
              onClick={async () => {
                setIsFsModal(false);
                await document.documentElement.requestFullscreen();
              }}
            >
              <FaExpand className="w-4 h-4" />
              Resume in Fullscreen
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
