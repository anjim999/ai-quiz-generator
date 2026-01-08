// src/components/Modal.jsx
import React, { useState, useEffect } from "react";
import { FaTimes, FaChartBar, FaListAlt } from "react-icons/fa";

export default function Modal({ open, onClose, title, scoreCard, assignmentDetails }) {
  const [tab, setTab] = useState("score");

  // Close on escape key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (open) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [open, onClose]);

  if (!open) return null;

  const tabs = [
    { id: 'score', label: 'Score Card', icon: FaChartBar },
    { id: 'details', label: 'Quiz Details', icon: FaListAlt }
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col animate-fade-in">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          <button
            className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center transition-colors cursor-pointer"
            onClick={onClose}
          >
            <FaTimes className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 px-6 pt-4 border-b border-slate-200">
          {tabs.map((t) => (
            <button
              key={t.id}
              className={`
                flex items-center gap-2 px-4 py-2.5 text-sm font-medium
                border-b-2 -mb-px transition-colors cursor-pointer
                ${tab === t.id
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
                }
              `}
              onClick={() => setTab(t.id)}
            >
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {tab === "score" ? scoreCard : assignmentDetails}
        </div>
      </div>
    </div>
  );
}
