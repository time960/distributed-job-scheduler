import time
import logging
import uuid
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from app.database import SessionLocal
from app.models.job import Job, JobStatus
from app.models.schedule import Schedule
from app.models.worker import WorkerNode, WorkerStatus
import socket

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("worker")

import socket
hostname = socket.gethostname()
WORKER_ID = f"worker-{hostname}"

from app.config import settings

def process_job(job_id: uuid.UUID, payload: dict):
    # Simulate work
    logger.info(f"[{WORKER_ID}] Processing job {job_id} with payload: {payload}")
    if payload.get("should_fail"):
        logger.error(f"[{WORKER_ID}] Job {job_id} failed artificially due to payload 'should_fail'")
        raise Exception("Artificial failure")
    sleep_duration = payload.get("sleep", 2)
    time.sleep(sleep_duration)
    logger.info(f"[{WORKER_ID}] Completed job {job_id}")

def run_worker():
    logger.info(f"[{WORKER_ID}] Starting worker loop...")
    hostname = socket.gethostname()
    
    # Registration with retry
    while True:
        try:
            with SessionLocal() as session:
                worker_node = session.query(WorkerNode).filter_by(worker_id=WORKER_ID).first()
                if worker_node:
                    worker_node.status = WorkerStatus.ACTIVE.name
                    worker_node.last_heartbeat_at = datetime.now(timezone.utc)
                    worker_node.updated_at = datetime.now(timezone.utc)
                    logger.info(f"[{WORKER_ID}] Existing worker node updated to ACTIVE.")
                else:
                    worker_node = WorkerNode(
                        worker_id=WORKER_ID,
                        hostname=hostname,
                        status=WorkerStatus.ACTIVE.name
                    )
                    session.add(worker_node)
                    logger.info(f"[{WORKER_ID}] New worker successfully registered.")
                session.commit()
                break
        except Exception as e:
            logger.error(f"[{WORKER_ID}] Failed to register worker: {e}. Retrying in 5s...")
            time.sleep(5)

    while True:
        try:
            with SessionLocal() as session:
                # Heartbeat and liveness check for workers
                try:
                    session.execute(
                        text("UPDATE workers SET status = 'ACTIVE', last_heartbeat_at = NOW(), updated_at = NOW() WHERE worker_id = :worker_id"),
                        {"worker_id": WORKER_ID}
                    )
                    session.execute(
                        text("UPDATE workers SET status = 'DEAD', updated_at = NOW() WHERE last_heartbeat_at < NOW() - INTERVAL '30 seconds' AND status = 'ACTIVE'")
                    )
                    session.commit()
                except Exception as e:
                    logger.error(f"[{WORKER_ID}] Heartbeat failed: {e}")

                # Sweeper for timed-out RUNNING jobs
                try:
                    session.execute(
                        text("""
                            UPDATE jobs 
                            SET status = 'PENDING', 
                                locked_by = NULL,
                                locked_at = NULL,
                                updated_at = NOW() 
                            WHERE status = 'RUNNING' 
                            AND locked_at < NOW() - make_interval(secs => :timeout)
                        """),
                        {"timeout": settings.job_timeout_seconds}
                    )
                    session.commit()
                except Exception as e:
                    logger.error(f"[{WORKER_ID}] Failed to sweep timed out jobs: {e}")

                # 1. Find and lock pending jobs using SKIP LOCKED (Batch Polling)
                query = text("""
                    UPDATE jobs
                    SET status = 'RUNNING', 
                        locked_by = :worker_id,
                        locked_at = NOW(),
                        attempts = attempts + 1,
                        updated_at = NOW()
                    WHERE id IN (
                        SELECT id FROM jobs 
                        WHERE status = 'PENDING' 
                        AND run_at <= NOW()
                        AND (next_retry_at IS NULL OR next_retry_at <= NOW())
                        ORDER BY priority DESC, run_at ASC, created_at ASC
                        FOR UPDATE SKIP LOCKED
                        LIMIT :batch_size
                    )
                    RETURNING id, payload, attempts, max_attempts;
                """)
                
                result = session.execute(query, {
                    "worker_id": WORKER_ID, 
                    "batch_size": settings.worker_batch_size
                })
                jobs_to_process = result.fetchall()
                session.commit()

                if jobs_to_process:
                    for job_row in jobs_to_process:
                        job_id, payload, attempts, max_attempts = job_row
                        try:
                            # 2. Process the job
                            process_job(job_id, payload)
                            
                            # 3. Mark as success
                            with SessionLocal() as update_session:
                                job = update_session.get(Job, job_id)
                                job.status = JobStatus.SUCCESS.name
                                job.completed_at = datetime.now(timezone.utc)
                                job.updated_at = datetime.now(timezone.utc)
                                update_session.execute(
                                    text("UPDATE workers SET jobs_processed = jobs_processed + 1 WHERE worker_id = :worker_id"),
                                    {"worker_id": WORKER_ID}
                                )
                                update_session.commit()
                        except Exception as e:
                            logger.error(f"[{WORKER_ID}] Error processing job {job_id}: {e}")
                            
                            # Apply retry logic
                            with SessionLocal() as update_session:
                                job = update_session.get(Job, job_id)
                                if job.attempts < job.max_attempts:
                                    # Retry
                                    delay_seconds = min(2 ** job.attempts, 300)
                                    jitter = random.uniform(0, 2)
                                    next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds + jitter)
                                    
                                    job.status = JobStatus.PENDING.name
                                    job.next_retry_at = next_retry
                                    job.error_message = str(e)
                                    job.locked_by = None
                                    job.locked_at = None
                                    job.updated_at = datetime.now(timezone.utc)
                                    logger.info(f"[{WORKER_ID}] Job {job_id} scheduled for retry at {next_retry}")
                                else:
                                    # DLQ
                                    job.status = JobStatus.DEAD_LETTER.name
                                    job.error_message = f"Max attempts reached. Last error: {str(e)}"
                                    job.locked_by = None
                                    job.locked_at = None
                                    job.completed_at = datetime.now(timezone.utc)
                                    job.updated_at = datetime.now(timezone.utc)
                                    logger.warning(f"[{WORKER_ID}] Job {job_id} moved to DEAD_LETTER")
                                    
                                update_session.commit()
                else:
                    # No job found, sleep before polling again
                    time.sleep(settings.worker_poll_interval_seconds)
        except Exception as e:
            logger.error(f"[{WORKER_ID}] Worker error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        run_worker()
    except KeyboardInterrupt:
        logger.info(f"[{WORKER_ID}] Worker stopping gracefully...")
        try:
            with SessionLocal() as session:
                session.execute(
                    text("UPDATE workers SET status = 'STOPPED', stopped_at = NOW(), updated_at = NOW() WHERE worker_id = :worker_id"),
                    {"worker_id": WORKER_ID}
                )
                session.commit()
        except Exception as e:
            logger.error(f"[{WORKER_ID}] Failed to update worker status on shutdown: {e}")
