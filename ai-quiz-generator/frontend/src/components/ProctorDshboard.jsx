import { useEffect, useRef, useState } from "react";

export default function ProctorDashboard(){
  const [sessionId, setSessionId] = useState("");
  const [events, setEvents] = useState([]);
  const wsRef = useRef(null);

  const connect = () => {
    if (!sessionId) return;
    const wsUrl = import.meta.env.VITE_API_URL?.replace(/^http/, 'ws') || "ws://127.0.0.1:8000";
    const ws = new WebSocket(`${wsUrl}/ws/proctor/${sessionId}`);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "event") {
          setEvents(e => [msg.event, ...e].slice(0,200));
        }
      } catch {}
    };
    wsRef.current = ws;
  };

  useEffect(() => () => { try { wsRef.current?.close(); } catch {} }, []);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Proctor Dashboard</h1>
      <div className="flex gap-2">
        <input className="input input-bordered" value={sessionId} onChange={e=>setSessionId(e.target.value)} placeholder="Enter session id"/>
        <button className="btn btn-primary" onClick={connect}>Connect</button>
      </div>
      <div className="card">
        <h3 className="font-semibold mb-2">Live Events</h3>
        <ul className="text-sm space-y-2 max-h-[60vh] overflow-auto">
          {events.map((ev, i)=>(
            <li key={i} className="border-b pb-2">
              <div className="flex justify-between">
                <span className="font-mono">{ev.at?.replace('T',' ').slice(0,19)}</span>
                <span className="badge">{ev.type}</span>
              </div>
              {ev.meta ? <pre className="text-xs mt-1 bg-gray-50 p-2 rounded">{JSON.stringify(ev.meta,null,2)}</pre> : null}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
