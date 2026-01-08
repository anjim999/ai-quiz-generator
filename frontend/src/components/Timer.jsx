// src/components/Timer.jsx
import { useEffect, useState } from "react";
import { FaClock } from "react-icons/fa";

export default function Timer({ totalSeconds, onEnd }) {
  const [left, setLeft] = useState(totalSeconds);

  useEffect(() => {
    if (left <= 0) {
      onEnd?.();
      return;
    }
    const id = setInterval(() => setLeft((l) => l - 1), 1000);
    return () => clearInterval(id);
  }, [left, onEnd]);

  const mins = Math.floor(left / 60);
  const secs = left % 60;

  // Determine timer state
  const isWarning = left <= 120 && left > 60; // Last 2 minutes
  const isDanger = left <= 60; // Last minute

  const timerClass = isDanger
    ? 'timer-danger'
    : isWarning
      ? 'timer-warning'
      : 'timer-normal';

  return (
    <div className={`timer ${timerClass} flex items-center gap-2`}>
      <FaClock className="w-4 h-4" />
      <span>
        {String(mins).padStart(2, "0")}:{String(secs).padStart(2, "0")}
      </span>
    </div>
  );
}
