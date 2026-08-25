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

    def shutdown(self) -> None:
        """Stop the scheduler safely."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)