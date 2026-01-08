// src/tabs/HistoryTab.jsx
import React, { useEffect, useState } from "react";
import { fetchHistory, fetchQuizById } from "../services/api";
import HistoryTable from "../components/HistoryTable";
import Modal from "../components/Modal";
import ScoreCard from "../components/ScoreCard";
import QuizDetails from "../components/QuizDetails";
import { FaSync, FaHistory, FaFolderOpen } from "react-icons/fa";

export default function HistoryTab() {
  const [rows, setRows] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [open, setOpen] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res = await fetchHistory();
      setRows(res.items || []);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleDetails(id) {
    try {
      const data = await fetchQuizById(id);
      setSelectedQuiz(data);
      setOpen(true);

      const saved = JSON.parse(localStorage.getItem("lastResult"));
      setLastResult(saved && saved.quizId === id ? saved : null);
    } catch (err) {
      console.error("Failed to load quiz details:", err);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FaHistory className="w-4 h-4 text-slate-400" />
          <h3 className="font-medium text-slate-900">Quiz History</h3>
          {rows.length > 0 && (
            <span className="badge badge-neutral">{rows.length}</span>
          )}
        </div>
        <button
          className="btn btn-ghost btn-sm"
          onClick={load}
          disabled={loading}
        >
          <FaSync className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="card card-body animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-12 bg-slate-100 rounded"></div>
            <div className="h-12 bg-slate-100 rounded"></div>
            <div className="h-12 bg-slate-100 rounded"></div>
          </div>
        </div>
      ) : rows.length === 0 ? (
        <div className="card card-body text-center py-12">
          <FaFolderOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-slate-900 mb-1">No quizzes yet</h4>
          <p className="text-sm text-slate-500">
            Generate your first quiz from a Wikipedia article to get started.
          </p>
        </div>
      ) : (
        <HistoryTable items={rows} onDetails={handleDetails} />
      )}

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={"Quiz Details"}
        scoreCard={<ScoreCard data={lastResult} />}
        assignmentDetails={<QuizDetails data={selectedQuiz} />}
      />
    </div>
  );
}
