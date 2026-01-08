// src/components/HistoryTable.jsx
import React from "react";
import { FaEye, FaCalendar, FaLink } from "react-icons/fa";

export default function HistoryTable({ items, onDetails }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="card overflow-hidden">
      <table className="min-w-full">
        <thead>
          <tr className="bg-slate-50 border-b border-slate-200">
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              Quiz
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider hidden md:table-cell">
              Source
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              Date
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items?.map((row) => (
            <tr key={row.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-6 py-4">
                <div>
                  <p className="font-medium text-slate-900 truncate max-w-xs">
                    {row.title}
                  </p>
                  <p className="text-xs text-slate-500">ID: {row.id}</p>
                </div>
              </td>
              <td className="px-6 py-4 hidden md:table-cell">
                <a
                  href={row.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-700 truncate max-w-xs"
                >
                  <FaLink className="w-3 h-3 flex-shrink-0" />
                  <span className="truncate">Wikipedia</span>
                </a>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <FaCalendar className="w-3 h-3 text-slate-400" />
                  {formatDate(row.date_generated)}
                </div>
              </td>
              <td className="px-6 py-4 text-right">
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => onDetails(row.id)}
                >
                  <FaEye className="w-3 h-3" />
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
