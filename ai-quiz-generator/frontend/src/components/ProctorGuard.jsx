// import { useCallback, useEffect, useRef, useState } from "react";

// export default function ProctorGuard({
//   sessionId,
//   maxStrikes = 3,
//   onAutoSubmit,
//   onStrikeChange
// }) {
//   const [fsOpen, setFsOpen] = useState(!!document.fullscreenElement);
//   const videoRef = useRef(null);
//   const streamRef = useRef(null);
//   const strikesRef = useRef({ tab: 0, fs: 0, total: 0 });
//   const debounceRef = useRef(0);

//   const postEvent = useCallback(async (type, meta={}) => {
//     if (!sessionId) return;
//     try {
//       await fetch(`${import.meta.env.VITE_API_URL}/session/${sessionId}/event`, {
//         method: "POST",
//         headers: {"Content-Type":"application/json"},
//         body: JSON.stringify({ type, meta })
//       });
//     } catch {}
//   }, [sessionId]);

//   const stopCam = useCallback(() => {
//     try { streamRef.current?.getTracks?.().forEach(t => t.stop()); } catch {}
//   }, []);

//   // Expose stop for QuizMode to call on submit
//   useEffect(() => {
//     window.__stopProctorCamera = stopCam;
//     return () => { delete window.__stopProctorCamera; };
//   }, [stopCam]);

//   const bump = useCallback(async (kind) => {
//     const now = Date.now();
//     if (now - debounceRef.current < 800) return; // debounce double events
//     debounceRef.current = now;

//     strikesRef.current[kind] += 1;
//     strikesRef.current.total += 1;
//     onStrikeChange?.({ ...strikesRef.current });

//     await postEvent(kind === "tab" ? "tab-blur" : "fs-exit", { ...strikesRef.current });

//     // RULES:
//     // 1) fs exit >= 1 and tab >= 1 => auto-submit
//     if (strikesRef.current.fs >= 1 && strikesRef.current.tab >= 1) {
//       onAutoSubmit?.("combo");
//       return;
//     }
//     // 2) total >= max → auto-submit
//     if (strikesRef.current.total >= maxStrikes) {
//       onAutoSubmit?.("max");
//     }
//   }, [maxStrikes, onAutoSubmit, onStrikeChange, postEvent]);

//   // Fullscreen watcher
//   useEffect(() => {
//     const onFs = () => {
//       const open = !!document.fullscreenElement;
//       setFsOpen(open);
//       if (open) postEvent("fs-enter");
//       else bump("fs");
//     };
//     document.addEventListener("fullscreenchange", onFs);
//     return () => document.removeEventListener("fullscreenchange", onFs);
//   }, [bump, postEvent]);

//   // Tab/visibility watcher
//   useEffect(() => {
//     const onVis = () => { if (document.hidden) bump("tab"); };
//     document.addEventListener("visibilitychange", onVis);
//     return () => document.removeEventListener("visibilitychange", onVis);
//   }, [bump]);

//   // Start camera once
//   useEffect(() => {
//     let cancelled = false;
//     (async () => {
//       try {
//         const s = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
//         if (cancelled) { s.getTracks().forEach(t => t.stop()); return; }
//         streamRef.current = s;
//         if (videoRef.current) videoRef.current.srcObject = s;
//       } catch (e) {
//         await postEvent("webcam-error", { message: String(e) });
//         onAutoSubmit?.("cam_denied");
//       }
//     })();
//     return () => { cancelled = true; stopCam(); };
//   }, [onAutoSubmit, postEvent, stopCam]);

//   // FS overlay when exited
//   if (!fsOpen) {
//     return (
//       <div className="fixed inset-0 z-[60] bg-black/70 flex items-center justify-center p-6">
//         <div className="bg-white rounded-xl p-6 max-w-md w-full text-center space-y-4">
//           <h3 className="text-lg font-semibold">Fullscreen Required</h3>
//           <p className="text-sm text-gray-600">You exited fullscreen. Re-enter to continue, or submit now.</p>
//           <div className="flex gap-3 justify-center">
//             <button
//               className="btn btn-primary"
//               onClick={() => document.documentElement.requestFullscreen()}
//             >
//               Re-enter Fullscreen
//             </button>
//             <button className="btn btn-ghost border" onClick={() => onAutoSubmit?.("fs_exit_prompt")}>
//               Submit & Exit
//             </button>
//           </div>
//         </div>
//       </div>
//     );
//   }

//   // Hidden video element just to keep stream alive
//   return <video ref={videoRef} className="hidden" autoPlay muted playsInline />;
// }
