import time
import logging
import uuid
import redis
from datetime import datetime, timezone
from croniter import croniter
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.schedule import Schedule
from app.models.job import Job, JobStatus
from app.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("scheduler")

SCHEDULER_ID = f"scheduler-{uuid.uuid4().hex[:8]}"

def calculate_next_run(cron_expression: str, start_time: datetime) -> datetime:
    cron = croniter(cron_expression, start_time)
    return cron.get_next(datetime)

def is_leader(redis_client):
    if redis_client.set("scheduler:leader", SCHEDULER_ID, nx=True, ex=10):
        return True
    if redis_client.get("scheduler:leader") == SCHEDULER_ID:
        redis_client.expire("scheduler:leader", 10)
        return True
    return False

def run_scheduler():
    logger.info(f"[{SCHEDULER_ID}] Starting scheduler loop...")
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    while True:
        try:
            with SessionLocal() as session:
                # Sweep for dead workers
                try:
                    session.execute(
                        text("UPDATE workers SET status = 'DEAD', updated_at = NOW() WHERE last_heartbeat_at < NOW() - INTERVAL '30 seconds' AND status = 'ACTIVE'")
                    )
                    session.commit()
                except Exception as e:
                    logger.error(f"[{SCHEDULER_ID}] Failed to sweep dead workers: {e}")

                if not is_leader(redis_client):
                    time.sleep(2)
                    continue

                # Find active schedules that are due to run
                query = text("""
                    SELECT id, name, cron_expression, payload, priority, max_attempts, next_run_at 
                    FROM schedules 
                    WHERE is_active = true 
                    AND next_run_at <= NOW()
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                """)
                
                result = session.execute(query)
                schedule_row = result.fetchone()
                
                if schedule_row:
                    s_id, name, cron_expr, payload, priority, max_attempts, next_run_at = schedule_row
                    
                    # Create job
                    new_job = Job(
                        name=f"{name}_{int(time.time())}",
                        payload=payload,
                        status=JobStatus.PENDING.name,
                        priority=priority,
                        max_attempts=max_attempts,
                        run_at=datetime.now(timezone.utc),
                        schedule_id=s_id,
                        scheduled_for=next_run_at
                    )
                    session.add(new_job)
                    
                    try:
                        session.commit()
                    except IntegrityError:
                        session.rollback()
                        logger.warning(f"[{SCHEDULER_ID}] Duplicate job prevented for schedule {s_id} at {next_run_at}")
                        
                        # Advance schedule clock safely
                        with SessionLocal() as update_session:
                            try:
                                next_run = calculate_next_run(cron_expr, next_run_at)
                                update_session.execute(
                                    text("UPDATE schedules SET next_run_at = :next_run, last_run_at = NOW() WHERE id = :s_id"),
                                    {"next_run": next_run, "s_id": s_id}
                                )
                                update_session.commit()
                            except Exception as e:
                                logger.error(f"[{SCHEDULER_ID}] Failed to advance schedule {s_id}: {e}")
                        continue
                    
                    # If job inserted successfully, advance the schedule clock
                    with SessionLocal() as update_session:
                        try:
                            next_run = calculate_next_run(cron_expr, next_run_at)
                            update_session.execute(
                                text("UPDATE schedules SET next_run_at = :next_run, last_run_at = NOW() WHERE id = :s_id"),
                                {"next_run": next_run, "s_id": s_id}
                            )
                            update_session.commit()
                            logger.info(f"[{SCHEDULER_ID}] Spawned job for schedule {s_id}. Next run at {next_run}")
                        except Exception as e:
                            logger.error(f"[{SCHEDULER_ID}] Failed to calculate next run for schedule {s_id}: {e}")
                            update_session.execute(
                                text("UPDATE schedules SET is_active = false WHERE id = :s_id"),
                                {"s_id": s_id}
                            )
                            update_session.commit()
                else:
                    # session.commit() handles rollback/closing implicitly
                    time.sleep(2)
        except Exception as e:
            logger.error(f"[{SCHEDULER_ID}] Scheduler error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        logger.info(f"[{SCHEDULER_ID}] Scheduler stopped.")
        # Release lock gracefully
        try:
            redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            if redis_client.get("scheduler:leader") == SCHEDULER_ID:
                redis_client.delete("scheduler:leader")
                logger.info(f"[{SCHEDULER_ID}] Released leader lock.")
        except Exception as e:
            pass
