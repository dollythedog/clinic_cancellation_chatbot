"""
Scheduler - APScheduler jobs for background tasks

This module sets up scheduled jobs:
- Check expired hold timers (every 30 seconds)
- Recalculate priority scores (every hour)

Author: Jonathan Ives (@dollythedog)
"""

import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.orchestrator import OfferOrchestrator
from app.core.prioritizer import update_all_priority_scores
from app.infra.db import session_scope
from app.infra.settings import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


def check_expired_holds_job():
    """
    Scheduled job to check for expired hold timers and send next batch.
    
    Runs every 30 seconds (configurable via HOLD_TIMER_CHECK_INTERVAL).
    """
    try:
        with session_scope() as session:
            orchestrator = OfferOrchestrator(session)
            batches_sent = orchestrator.check_expired_holds()
            
            if batches_sent > 0:
                logger.info(f"⏰ Expired holds check: Sent {batches_sent} new batches")
            
    except Exception as e:
        logger.error(f"Error in check_expired_holds_job: {e}", exc_info=True)


def recalculate_priorities_job():
    """
    Scheduled job to recalculate priority scores for all active waitlist entries.
    
    Runs every hour (configurable via PRIORITY_RECALC_INTERVAL).
    """
    try:
        with session_scope() as session:
            if settings.ENABLE_PRIORITY_RECALC:
                count = update_all_priority_scores(session, active_only=True)
                logger.info(f"📊 Priority recalculation: Updated {count} entries")
            else:
                logger.debug("Priority recalculation disabled by settings")
            
    except Exception as e:
        logger.error(f"Error in recalculate_priorities_job: {e}", exc_info=True)


def init_scheduler():
    """
    Initialize and start the APScheduler.
    
    This should be called on application startup.
    
    Example:
        >>> init_scheduler()
        >>> # Scheduler is now running background jobs
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return scheduler
    
    scheduler = AsyncIOScheduler()
    
    # Job 1: Check expired hold timers (every 30 seconds)
    scheduler.add_job(
        check_expired_holds_job,
        trigger=IntervalTrigger(seconds=settings.HOLD_TIMER_CHECK_INTERVAL),
        id="check_expired_holds",
        name="Check expired hold timers",
        replace_existing=True,
        misfire_grace_time=10
    )
    logger.info(f"✅ Scheduled job: check_expired_holds (every {settings.HOLD_TIMER_CHECK_INTERVAL}s)")
    
    # Job 2: Recalculate priority scores (every hour)
    scheduler.add_job(
        recalculate_priorities_job,
        trigger=IntervalTrigger(minutes=settings.PRIORITY_RECALC_INTERVAL),
        id="recalculate_priorities",
        name="Recalculate waitlist priorities",
        replace_existing=True,
        misfire_grace_time=60
    )
    logger.info(f"✅ Scheduled job: recalculate_priorities (every {settings.PRIORITY_RECALC_INTERVAL}m)")
    
    # Start scheduler
    scheduler.start()
    logger.info("🚀 APScheduler started")
    
    return scheduler


def shutdown_scheduler():
    """
    Shutdown the scheduler gracefully.
    
    This should be called on application shutdown.
    
    Example:
        >>> shutdown_scheduler()
        >>> # Scheduler stopped, all jobs canceled
    """
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown(wait=True)
        logger.info("🛑 APScheduler shutdown complete")
        scheduler = None
    else:
        logger.warning("Scheduler not initialized, nothing to shutdown")


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """
    Get the global scheduler instance.
    
    Returns:
        AsyncIOScheduler: Scheduler instance, or None if not initialized
    """
    return scheduler


def pause_scheduler():
    """Pause all scheduled jobs"""
    if scheduler:
        scheduler.pause()
        logger.info("⏸️  Scheduler paused")


def resume_scheduler():
    """Resume all scheduled jobs"""
    if scheduler:
        scheduler.resume()
        logger.info("▶️  Scheduler resumed")


def list_jobs() -> list:
    """
    List all scheduled jobs with their next run times.
    
    Returns:
        list: Job details
    """
    if not scheduler:
        return []
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time,
            "trigger": str(job.trigger)
        })
    
    return jobs
