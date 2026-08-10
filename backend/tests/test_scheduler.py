from app.services.scheduler.service import ScholarshipScheduler
from app.config.settings import settings

def test_scheduler_rejects_invalid_interval() -> None:
    def job() -> None:
        pass

    try:
        ScholarshipScheduler(job, interval_hours=0)
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid interval")


def test_scheduler_registers_pipeline_job() -> None:
    calls = []

    def job() -> None:
        calls.append("called")

    scheduler = ScholarshipScheduler(
        job,
        interval_hours=6,
    )

    scheduler.start()

    try:
        jobs = scheduler._scheduler.get_jobs()

        assert len(jobs) == 1
        assert jobs[0].id == "scholarship_discovery"
        assert jobs[0].trigger.interval.total_seconds() == 6 * 60 * 60

    finally:
        scheduler.shutdown()

    from app.config.settings import settings


def test_scheduler_interval_is_configured() -> None:
    assert settings.SCHEDULER_INTERVAL_HOURS == 6