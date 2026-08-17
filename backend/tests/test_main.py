import pytest

from app import main


def test_scheduled_job_runs_discovery(monkeypatch) -> None:
    calls = []

    async def fake_run_scheduled_discovery() -> None:
        calls.append("called")

    monkeypatch.setattr(
        main,
        "run_scheduled_discovery",
        fake_run_scheduled_discovery,
    )

    main.scheduled_job()

    assert calls == ["called"]

@pytest.mark.asyncio
async def test_manual_discovery_runs_discovery(monkeypatch) -> None:
    calls = []

    async def fake_run_scheduled_discovery() -> None:
        calls.append("called")

    monkeypatch.setattr(
        main,
        "run_scheduled_discovery",
        fake_run_scheduled_discovery,
    )

    response = await main.manual_discovery()

    assert response == {
        "status": "completed",
        "message": "Scholarship discovery completed",
    }

    assert calls == ["called"]