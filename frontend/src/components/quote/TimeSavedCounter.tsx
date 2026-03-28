"use client";
import { useEffect, useState } from "react";
import { Clock } from "lucide-react";

interface Props {
  startTime: number;
  isRunning: boolean;
  minutesSaved?: number;
}

export default function TimeSavedCounter({ startTime, isRunning, minutesSaved }: Props) {
  const [elapsed, setElapsed] = useState(0);
  const humanSeconds = (minutesSaved ?? 150) * 60;

  useEffect(() => {
    if (!isRunning) return;
    const t = setInterval(() => setElapsed(Math.floor((Date.now() - startTime) / 1000)), 1000);
    return () => clearInterval(t);
  }, [isRunning, startTime]);

  const savedSeconds = humanSeconds - elapsed;
  const savedMins = Math.floor(savedSeconds / 60);
  const savedHrs  = Math.floor(savedMins / 60);
  const remMins   = savedMins % 60;

  const fmt = (s: number) => String(s).padStart(2, "0");
  const elapsedStr = `${fmt(Math.floor(elapsed / 60))}:${fmt(elapsed % 60)}`;
  const savedStr   = savedHrs > 0 ? `${savedHrs}h ${remMins}m` : `${savedMins}m`;

  return (
    <div className="bg-brand-slate border border-slate-700 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <Clock className="w-4 h-4 text-green-400" />
        <span className="text-xs text-slate-400 uppercase tracking-wide font-semibold">Time Intelligence</span>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-slate-500 mb-1">ProcureIQ time</p>
          <p className="text-2xl font-black font-mono text-white">{elapsedStr}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 mb-1">You saved</p>
          <p className="text-2xl font-black text-green-400">
            {isRunning ? `~${savedStr}` : minutesSaved ? `${Math.floor(minutesSaved / 60)}h ${minutesSaved % 60}m` : "—"}
          </p>
        </div>
      </div>
      <div className="mt-3">
        <div className="flex justify-between text-xs text-slate-500 mb-1">
          <span>Progress vs human</span>
          <span>{Math.min(100, Math.round((elapsed / humanSeconds) * 100))}% of human time</span>
        </div>
        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-400 rounded-full transition-all duration-1000"
            style={{ width: `${Math.min(100, (elapsed / humanSeconds) * 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}
