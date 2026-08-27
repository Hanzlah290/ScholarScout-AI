from __future__ import annotations

from typing import Callable, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.scheduler.discovery_job import (
    run_scheduled_discovery,
    run_scheduled_source_discovery,
)


class ScholarshipScheduler:
    """Schedules scholarship pipeline executions and periodic source discovery."""

    def __init__(self, interval_hours: int = 6) -> None:
        if interval_hours <= 0:
            raise ValueError("interval_hours must be greater than zero")
        self.interval_hours = interval_hours
        self._scheduler: Optional[AsyncIOScheduler] = None

    def start(self) -> None:
        """Start the async background scheduler."""
        self._scheduler = AsyncIOScheduler()

        # Job 1: 6-Hour Heartbeat for Due Sources
        self._scheduler.add_job(
            run_scheduled_discovery,
            "interval",
            hours=self.interval_hours,
            id="scholarship_due_processing",
            replace_existing=True,
        )

        # Job 2: 24-Hour Source Discovery (Find new university websites)
        self._scheduler.add_job(
            run_scheduled_source_discovery,
            "interval",
            hours=24,
            id="university_source_discovery",
            replace_existing=True,
        )

        self._scheduler.start()

    def get_status(self) -> dict:
        """Returns the live status and next execution timestamp of the pipeline job."""
        if not self._scheduler or not self._scheduler.running:
            return {
                "running": False,
                "status": "stopped",
                "next_run_at": None,
            }

        job = self._scheduler.get_job("scholarship_due_processing")
        next_run = job.next_run_time.isoformat() if (job and job.next_run_time) else None

        return {
            "running": True,
            "status": "waiting",
            "next_run_at": next_run,
        }

    def shutdown(self) -> None:
        """Stop the scheduler safely."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)


# Global singleton instance for access across FastAPI routes
scheduler_instance = ScholarshipScheduler()