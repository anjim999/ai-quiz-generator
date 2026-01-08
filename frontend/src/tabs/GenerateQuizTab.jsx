// src/tabs/GenerateQuizTab.jsx
import { useState } from "react";
import { generateQuiz } from "../services/api";
import QuizDisplay from "../components/QuizDisplay";
import { useNavigate } from "react-router-dom";
import { FaPlay, FaSpinner, FaLink, FaInfoCircle } from "react-icons/fa";

const COUNTS = [5, 10, 15, 20, 30, 40, 50];

export default function GenerateQuizTab() {
  const [url, setUrl] = useState("");
  const [count, setCount] = useState(10);
  const [hideAnswers, setHideAnswers] = useState(false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleGenerate() {
    setError("");
    const trimmed = url.trim();

    if (!trimmed) {
      setError("Please enter a Wikipedia URL");
      return;
    }

    const wikiPattern = /^https?:\/\/(en\.)?wikipedia\.org\/(wiki|w)\/?/i;
    if (!wikiPattern.test(trimmed)) {
      setError("Please enter a valid Wikipedia URL (e.g., https://en.wikipedia.org/wiki/...)");
      return;
    }

    let title;
    try {
      const u = new URL(trimmed);
      if (u.pathname.startsWith("/wiki/")) {
        title = u.pathname.split("/wiki/")[1];
      } else {
        title = u.searchParams.get("title");
      }
      if (!title) throw new Error("no title");
    } catch (err) {
      setError("Unable to parse Wikipedia URL. Please enter a valid URL.");
      return;
    }

    try {
      const encodedTitle = encodeURIComponent(title);
      const check = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodedTitle}`);
      if (!check.ok) {
        setError("Wikipedia article not found. Please check the URL.");
        return;
      }
      const info = await check.json();
      if (info.type === "https://mediawiki.org/wiki/HyperSwitch/errors/not_found") {
        setError("Wikipedia article does not exist. Please try another URL.");
        return;
      }
    } catch (e) {
      setError("Unable to validate Wikipedia page. Please check your internet connection.");
      return;
    }

    setLoading(true);
    setData(null);

    try {
      const res = await generateQuiz(trimmed, hideAnswers, count);
      setData(res);
      localStorage.setItem("activeQuiz", JSON.stringify(res));
    } catch (err) {
      console.error("Quiz generation failed:", err);
      setError("Quiz generation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="card card-body">
        <div className="space-y-5">
          {/* URL Input */}
          <div>
            <label className="label">
              <FaLink className="inline w-3 h-3 mr-1.5" />
              Wikipedia Article URL
            </label>
            <input
              className={`input ${error ? 'input-error' : ''}`}
              placeholder="https://en.wikipedia.org/wiki/Alan_Turing"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                setError("");
              }}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
            />
            {error && (
              <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                <FaInfoCircle className="w-3 h-3" />
                {error}
              </p>
            )}
          </div>

          {/* Options Row */}
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="label">Number of Questions</label>
              <select
                className="select"
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
              >
                {COUNTS.map((n) => (
                  <option key={n} value={n}>
                    {n} questions
                  </option>
                ))}
              </select>
            </div>

            <button
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? (
                <>
                  <FaSpinner className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  Generate Quiz
                </>
              )}
            </button>

            {data && (
              <button
                className="btn btn-success"
                onClick={() => navigate("/exam")}
              >
                <FaPlay className="w-3 h-3" />
                Start Exam
              </button>
            )}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="mt-6 p-6 border border-slate-200 rounded-lg bg-slate-50">
            <div className="flex items-center gap-3">
              <FaSpinner className="w-5 h-5 animate-spin text-indigo-600" />
              <div>
                <p className="font-medium text-slate-900">Generating your quiz...</p>
                <p className="text-sm text-slate-500">
                  This may take 10-30 seconds depending on article length
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Quiz Display */}
      {data && !loading && (
        <div className="animate-fade-in">
          <QuizDisplay data={data} hideAnswers={hideAnswers} />
        </div>
      )}

      {/* Sample URLs Hint */}
      {!data && !loading && (
        <div className="card card-body">
          <h3 className="text-sm font-medium text-slate-700 mb-3">
            Sample URLs to try:
          </h3>
          <div className="flex flex-wrap gap-2">
            {[
              "Alan_Turing",
              "Artificial_intelligence",
              "Python_(programming_language)",
              "Albert_Einstein"
            ].map((topic) => (
              <button
                key={topic}
                onClick={() => setUrl(`https://en.wikipedia.org/wiki/${topic}`)}
                className="text-xs px-3 py-1.5 rounded-full border border-slate-200 
                         text-slate-600 hover:bg-slate-50 hover:border-slate-300
                         transition-colors cursor-pointer"
              >
                {topic.replace(/_/g, " ").replace(/\(.*\)/, "")}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
