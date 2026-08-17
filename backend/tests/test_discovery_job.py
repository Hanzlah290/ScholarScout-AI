from uuid import uuid4

import pytest

from app.models.source import Source
from app.services.scheduler import discovery_job


@pytest.mark.asyncio
async def test_scheduled_discovery_runs_enabled_sources(
    monkeypatch,
) -> None:
    enabled_source = Source(
        id=uuid4(),
        name="Enabled University",
        base_url="https://enabled.example.edu.cn",
        source_type="university",
        enabled=True,
        status="active",
    )

    disabled_source = Source(
        id=uuid4(),
        name="Disabled University",
        base_url="https://disabled.example.edu.cn",
        source_type="university",
        enabled=False,
        status="active",
    )

    class FakeResult:
        def all(self):
            return [
            enabled_source,
        ]

    class FakeSession:
        def __init__(self):
            self.closed = False

        def scalars(self, statement):
            return FakeResult()

        def close(self):
            self.closed = True

    fake_db = FakeSession()

    class FakePipeline:
        def __init__(self):
            self.sources = []

        async def run(self, db, source):
            self.sources.append(source)

    fake_pipeline = FakePipeline()

    monkeypatch.setattr(
        discovery_job,
        "SessionLocal",
        lambda: fake_db,
    )

    monkeypatch.setattr(
        discovery_job,
        "build_pipeline",
        lambda: fake_pipeline,
    )

    await discovery_job.run_scheduled_discovery()

    assert fake_pipeline.sources == [
        enabled_source,
    ]

    assert fake_db.closed is True