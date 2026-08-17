from __future__ import annotations

from collections.abc import Callable


class ScholarshipScheduler:
    """Schedule scholarship discovery pipeline executions."""

    def __init__(
        self,
        job: Callable[[], None],
        interval_hours: int = 6,
    ) -> None:
        if interval_hours <= 0:
            raise ValueError("interval_hours must be greater than zero")

        self.job = job
        self.interval_hours = interval_hours

    def start(self) -> None:
        """Start the scheduled execution."""
        from apscheduler.schedulers.background import BackgroundScheduler

        self._scheduler = BackgroundScheduler()

        self._scheduler.add_job(
            self.job,
            "interval",
            hours=self.interval_hours,
            id="scholarship_discovery",
            replace_existing=True,
        )

        self._scheduler.start()

    def shutdown(self) -> None:
        """Stop the scheduler."""
        if hasattr(self, "_scheduler"):
            self._scheduler.shutdown(wait=False)