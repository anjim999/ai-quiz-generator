// src/pages/Dashboard.jsx
import { useState } from "react";
import GenerateQuizTab from "../tabs/GenerateQuizTab";
import HistoryTab from "../tabs/HistoryTab";
import Navbar from "../components/Navbar";
import { FaPlus, FaHistory } from "react-icons/fa";

const Dashboard = () => {
  const [tab, setTab] = useState("generate");

  const tabs = [
    { id: "generate", label: "Generate Quiz", icon: FaPlus },
    { id: "history", label: "Quiz History", icon: FaHistory }
  ];

  return (
    <>
      <Navbar />
      <main className="page-padding">
        <div className="container-wide py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-heading text-slate-900 mb-1">Quiz Dashboard</h1>
            <p className="text-body">
              Generate AI-powered quizzes from Wikipedia articles
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-2 mb-8 border-b border-slate-200">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 text-sm font-medium
                  border-b-2 -mb-px transition-colors duration-200 cursor-pointer
                  ${tab === t.id
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
                  }
                `}
              >
                <t.icon className="w-4 h-4" />
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="animate-fade-in">
            {tab === "generate" ? <GenerateQuizTab /> : <HistoryTab />}
          </div>
        </div>
      </main>
    </>
  );
};

export default Dashboard;