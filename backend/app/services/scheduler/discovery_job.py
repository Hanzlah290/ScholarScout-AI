from __future__ import annotations

import logging
from threading import Lock

from app.database.session import SessionLocal
from app.services.automation.manager import AutomationManager

logger = logging.getLogger(__name__)


class DiscoveryAlreadyRunning(RuntimeError):
    """Raised when a second discovery run is requested in this process."""


_discovery_lock = Lock()
_manager = AutomationManager()


async def run_scheduled_discovery() -> None:
    """
    Heartbeat job running every 6 hours.
    Queries PostgreSQL for due sources and executes the scholarship discovery pipeline.
    """
    if not _discovery_lock.acquire(blocking=False):
        logger.warning("[SCHEDULER] A discovery run is already in progress. Skipping cycle.")
        raise DiscoveryAlreadyRunning("A discovery run is already in progress")

    try:
        logger.info("[SCHEDULER] Heartbeat triggered. Querying due sources...")
        with SessionLocal() as db:
            processed = await _manager.process_due_sources(db)
            logger.info(f"[SCHEDULER] Completed heartbeat processing for {processed} due sources.")
    finally:
        _discovery_lock.release()


async def run_scheduled_source_discovery() -> None:
    """
    Discovery job running every 24 hours.
    Executes search queries to find new university portals and seeds them into PostgreSQL.
    """
    logger.info("[SCHEDULER] Triggering 24-hour university source discovery...")
    try:
        with SessionLocal() as db:
            new_sources = await _manager.run_discovery_cycle(db)
            logger.info(f"[SCHEDULER] Discovery completed. Added {len(new_sources)} new sources to database.")
    except Exception as exc:
        logger.error(f"[SCHEDULER] Source discovery cycle failed: {exc}")