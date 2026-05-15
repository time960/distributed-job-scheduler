from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
import redis
from app.config import settings
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(tags=["Metrics"])

# Define Gauges
JOBS_TOTAL = Gauge('jobs_total', 'Total jobs by status', ['status'])
JOB_RETRY_TOTAL = Gauge('job_retry_total', 'Total job retry attempts')
WORKERS_TOTAL = Gauge('workers_total', 'Total workers by status', ['status'])
SCHEDULER_LEADER = Gauge('scheduler_leader', 'Is scheduler leader active')
JOB_PROCESSING_DURATION = Gauge('job_processing_duration_seconds', 'Average job processing duration (success jobs last 5 mins)')

@router.get("/metrics")
def get_metrics(session: Session = Depends(get_db)):
    # 1. Update Job Counts
    jobs_result = session.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM jobs 
        GROUP BY status
    """))
    
    # Reset all statuses to 0 first to avoid stale labels
    for s in ['pending', 'running', 'success', 'failed', 'canceled', 'dead_letter']:
        JOBS_TOTAL.labels(status=s).set(0)
        
    for row in jobs_result:
        JOBS_TOTAL.labels(status=row.status.lower()).set(row.count)
        
    # 2. Update Job Retries
    retry_result = session.execute(text("SELECT COALESCE(SUM(attempts), 0) FROM jobs"))
    JOB_RETRY_TOTAL.set(retry_result.scalar())
    
    # 3. Update Workers
    workers_result = session.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM workers 
        GROUP BY status
    """))
    
    for s in ['active', 'dead', 'stopped']:
        WORKERS_TOTAL.labels(status=s).set(0)
        
    for row in workers_result:
        WORKERS_TOTAL.labels(status=row.status.lower()).set(row.count)
        
    # 4. Processing Duration
    duration_result = session.execute(text("""
        SELECT COALESCE(AVG(EXTRACT(EPOCH FROM (completed_at - locked_at))), 0) 
        FROM jobs 
        WHERE status = 'SUCCESS' 
        AND completed_at >= NOW() - INTERVAL '5 minutes'
    """))
    JOB_PROCESSING_DURATION.set(duration_result.scalar())
    
    # 5. Scheduler Leader
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
        is_leader = 1 if r.exists("scheduler:leader") else 0
        SCHEDULER_LEADER.set(is_leader)
    except Exception:
        SCHEDULER_LEADER.set(0)

    # Return prometheus format
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/metrics/simple")
def get_metrics_simple(session: Session = Depends(get_db)):
    jobs_result = session.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM jobs 
        GROUP BY status
    """)).fetchall()
    
    workers_result = session.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM workers 
        GROUP BY status
    """)).fetchall()

    metrics = {
        "jobs": {
            "total": 0,
            "pending": 0,
            "running": 0,
            "success": 0,
            "failed": 0,
            "canceled": 0,
            "dead_letter": 0
        },
        "workers": {
            "active": 0,
            "dead": 0,
            "stopped": 0
        }
    }
    
    for row in jobs_result:
        status = row.status.lower()
        if status in metrics["jobs"]:
            metrics["jobs"][status] = row.count
            metrics["jobs"]["total"] += row.count
            
    for row in workers_result:
        status = row.status.lower()
        if status in metrics["workers"]:
            metrics["workers"][status] = row.count
            
    return metrics
