import { authHeaders } from "../services/api";

export default function PDFExportButton({ quizId, count, durationStr }) {
  const handle = async () => {
    try {
      const headers = authHeaders({ "Content-Type": "application/json" });
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/api/quiz/export_pdf/${quizId}`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({ user: "Candidate", count, duration_str: durationStr }),
        }
      );

      if (res.status === 401) {
        alert("Unauthorized: please log in to download the PDF.");
        return;
      }

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        alert(`Failed to get PDF: ${res.status} ${text}`);
        return;
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `quiz_${quizId}.pdf`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      console.error("PDF download error:", err);
      alert("Failed to download PDF");
    }
  };

  return (
    <button className="btn btn-outline" onClick={handle}>
      Export PDF
    </button>
  );
}
