"use client";

import { useEffect, useState } from "react";

interface NavbarProps {
  lastScanAt?: string | null;
  nextRunAt?: string | null;
  isSchedulerRunning?: boolean;
}

export default function Navbar({
  lastScanAt,
  nextRunAt,
  isSchedulerRunning = false,
}: NavbarProps) {
  const [timeLeft, setTimeLeft] = useState<string>("--h --m --s");

  useEffect(() => {
    if (!nextRunAt) {
      setTimeLeft("Not scheduled");
      return;
    }

    const updateTimer = () => {
      const targetTime = new Date(nextRunAt).getTime();
      const now = new Date().getTime();
      const difference = targetTime - now;

      if (difference <= 0) {
        setTimeLeft("Pipeline starting...");
        return;
      }

      const hours = Math.floor((difference / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((difference / 1000 / 60) % 60);
      const seconds = Math.floor((difference / 1000) % 60);

      setTimeLeft(
        `${String(hours).padStart(2, "0")}h ${String(minutes).padStart(
          2,
          "0"
        )}m ${String(seconds).padStart(2, "0")}s`
      );
    };

    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);

    return () => clearInterval(timerInterval);
  }, [nextRunAt]);

  const formattedLastScan = lastScanAt
    ? new Date(lastScanAt).toLocaleString()
    : "Just now";

  return (
    <header className="flex flex-col gap-4 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-xl font-semibold">🎓 ScholarScout AI</h1>
        <p className="text-sm text-muted-foreground">
          China Scholarship Dashboard
        </p>
      </div>

      <div className="flex flex-col items-start gap-2 sm:items-end sm:flex-row sm:gap-6 text-sm text-muted-foreground">
        {/* Scheduler Pipeline Status Badge */}
        <div className="flex items-center gap-2">
          <span className="text-xs">Pipeline:</span>
          {isSchedulerRunning ? (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              Active (Next in {timeLeft})
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-medium text-amber-600 dark:text-amber-400 border border-amber-500/20">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              Idle / Manual Mode
            </span>
          )}
        </div>

        {/* Last Scan Display */}
        <div>
          Last Scan:{" "}
          <span className="font-medium text-foreground">
            {formattedLastScan}
          </span>
        </div>
      </div>
    </header>
  );
}