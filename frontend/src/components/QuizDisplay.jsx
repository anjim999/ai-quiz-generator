// src/components/QuizDisplay.jsx
import React, { useMemo, useState } from "react";
import { FaUser, FaBuilding, FaMapMarkerAlt, FaLink, FaTags } from "react-icons/fa";

export default function QuizDisplay({ data, takeMode = false }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const score = useMemo(() => {
    if (!submitted) return 0;
    return data.quiz.reduce((acc, q, idx) => acc + (answers[idx] === q.answer ? 1 : 0), 0);
  }, [submitted, answers, data]);

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Article Info Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Summary Card */}
        <div className="card card-body">
          <h2 className="text-lg font-semibold text-slate-900 mb-2">{data.title}</h2>
          <a
            href={data.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-700 mb-3"
          >
            <FaLink className="w-3 h-3" />
            View on Wikipedia
          </a>
          <p className="text-sm text-slate-600 leading-relaxed">{data.summary}</p>

          {data.sections?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <p className="text-xs font-medium text-slate-500 uppercase mb-2">Sections</p>
              <div className="flex flex-wrap gap-2">
                {data.sections?.slice(0, 6).map((s, i) => (
                  <span key={i} className="badge badge-neutral">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Key Entities Card */}
        <div className="card card-body">
          <h3 className="font-semibold text-slate-900 mb-4">Key Entities</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <FaUser className="w-4 h-4 text-slate-400 mt-0.5" />
              <div>
                <span className="font-medium text-slate-700">People: </span>
                <span className="text-slate-600">
                  {data.key_entities?.people?.join(", ") || "—"}
                </span>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <FaBuilding className="w-4 h-4 text-slate-400 mt-0.5" />
              <div>
                <span className="font-medium text-slate-700">Organizations: </span>
                <span className="text-slate-600">
                  {data.key_entities?.organizations?.join(", ") || "—"}
                </span>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <FaMapMarkerAlt className="w-4 h-4 text-slate-400 mt-0.5" />
              <div>
                <span className="font-medium text-slate-700">Locations: </span>
                <span className="text-slate-600">
                  {data.key_entities?.locations?.join(", ") || "—"}
                </span>
              </div>
            </div>
          </div>

          {data.related_topics?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <div className="flex items-center gap-2 mb-2">
                <FaTags className="w-3 h-3 text-slate-400" />
                <span className="text-xs font-medium text-slate-500 uppercase">Related Topics</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {data.related_topics?.map((t, i) => (
                  <span key={i} className="badge badge-primary">{t}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quiz Questions */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h3 className="font-semibold text-slate-900">Generated Questions</h3>
          <span className="badge badge-neutral">{data.quiz?.length || 0} questions</span>
        </div>

        <div className="card-body space-y-6">
          {data.quiz?.map((q, idx) => (
            <div key={idx} className="pb-6 border-b border-slate-100 last:border-0 last:pb-0">
              <div className="flex items-start gap-3 mb-4">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-slate-100 
                               flex items-center justify-center text-sm font-medium text-slate-600">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`badge ${q.difficulty === 'easy' ? 'badge-success' :
                        q.difficulty === 'medium' ? 'badge-warning' : 'badge-danger'
                      }`}>
                      {q.difficulty}
                    </span>
                  </div>
                  <p className="font-medium text-slate-900">{q.question}</p>
                </div>
              </div>

              <div className="ml-10 space-y-2">
                {q.options.map((opt, i) => {
                  const id = `q${idx}-opt${i}`;
                  const checked = answers[idx] === opt;
                  const letters = ['A', 'B', 'C', 'D'];

                  return (
                    <label
                      key={id}
                      htmlFor={id}
                      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer
                                transition-all duration-200
                                ${takeMode
                          ? checked
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                          : 'border-slate-200 bg-slate-50 cursor-default'
                        }`}
                    >
                      <span className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center 
                                     text-xs font-medium text-slate-600">
                        {letters[i]}
                      </span>
                      {takeMode && (
                        <input
                          id={id}
                          type="radio"
                          name={`q-${idx}`}
                          checked={checked}
                          onChange={() => setAnswers(a => ({ ...a, [idx]: opt }))}
                          className="sr-only"
                        />
                      )}
                      <span className="text-sm text-slate-700">{opt}</span>
                    </label>
                  );
                })}
              </div>

              {takeMode && submitted && (
                <div className="ml-10 mt-3 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <p className={`text-sm font-medium ${answers[idx] === q.answer ? 'text-emerald-600' : 'text-red-600'}`}>
                    {answers[idx] === q.answer ? '✓ Correct' : '✗ Incorrect'}
                    <span className="ml-2 text-slate-600">
                      Answer: <span className="font-semibold">{q.answer}</span>
                    </span>
                  </p>
                  <p className="text-sm text-slate-600 mt-1">{q.explanation}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
