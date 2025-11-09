import { useCallback, useEffect, useRef, useState } from "react";

export default function ProctorGuard({
  sessionId,
  maxStrikes = 3,
  onAutoSubmit,
  onStrikeChange
}) {
  const [fsOpen, setFsOpen] = useState(document.fullscreenElement != null);
  const [videoStream, setVideoStream] = useState(null);
  const strikes = useRef({ tab: 0, fs: 0, total: 0 });
  const debounceRef = useRef(0);

  // helper: send event to backend
  const postEvent = useCallback(async (type, meta={}) => {
    if (!sessionId) return;
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/session/${sessionId}/event`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ type, meta })
      });
    } catch {}
  }, [sessionId]);

  // prevent double count within 800ms
  const bump = useCallback(async (kind) => {
    const now = Date.now();
    if (now - debounceRef.current < 800) return; // debounce
    debounceRef.current = now;

    strikes.current[kind] += 1;
    strikes.current.total += 1;
    onStrikeChange?.(strikes.current);

    await postEvent(kind === "tab" ? "tab-blur" : "fs-exit", { ...strikes.current });

    // rule: if fs exit ≥ 1 AND tab switch ≥ 1 → auto submit
    if (strikes.current.fs >= 1 && strikes.current.tab >= 1) {
      onAutoSubmit?.("rule_combo");
      return;
    }
    // rule: total ≥ 3 → auto submit
    if (strikes.current.total >= maxStrikes) {
      onAutoSubmit?.("rule_total");
    }
  }, [maxStrikes, onAutoSubmit, onStrikeChange, postEvent]);

  // fullscreen listeners
  useEffect(() => {
    const onFsChange = () => {
      const open = document.fullscreenElement != null;
      setFsOpen(open);
      if (open) {
        postEvent("fs-enter");
      } else {
        bump("fs");
      }
    };
    document.addEventListener("fullscreenchange", onFsChange);
    return () => document.removeEventListener("fullscreenchange", onFsChange);
  }, [bump, postEvent]);

  // tab/visibility listeners (single strike source = visibility)
  useEffect(() => {
    const onVis = () => {
      if (document.hidden) bump("tab");
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [bump]);

  // webcam start
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        if (!cancelled) setVideoStream(stream);
      } catch (e) {
        // still continue exam but log
        postEvent("webcam-error", { message: String(e) });
      }
    })();
    return () => { cancelled = true; };
  }, [postEvent]);

  // expose a stop method on window for submit() to call
  useEffect(() => {
    window.__stopProctorCamera = () => {
      try {
        videoStream?.getTracks()?.forEach(t => t.stop());
      } catch {}
    };
  }, [videoStream]);

  // UI overlay when fullscreen exited
  if (!fsOpen) {
    return (
      <div className="fixed inset-0 z-[60] bg-black/70 flex items-center justify-center p-6">
        <div className="bg-white rounded-xl p-6 max-w-md w-full text-center space-y-4">
          <h3 className="text-lg font-semibold">Fullscreen Required</h3>
          <p className="text-sm text-gray-600">
            You exited fullscreen during the exam. Re-enter to continue, or submit now.
          </p>
          <div className="flex gap-3 justify-center">
            <button
              className="btn btn-primary"
              onClick={() => document.documentElement.requestFullscreen()}
            >
              Re-enter Fullscreen
            </button>
            <button className="btn btn-ghost border" onClick={() => onAutoSubmit?.("fs_exit_prompt")}>
              Submit & Exit
            </button>
          </div>
        </div>
      </div>
    );
  }

  // tiny hidden video element (stream active) – no UI shown
  return (
    <video
      className="hidden"
      autoPlay
      muted
      playsInline
      ref={el => { if (el && videoStream) el.srcObject = videoStream; }}
    />
  );
}
