from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import redis
from app.config import settings
from app.models.job import Job, JobStatus
from app.models.schedule import Schedule
from app.services.worker_service import WorkerService

router = APIRouter()

def get_worker_service(db: Session = Depends(get_db)) -> WorkerService:
    from app.services.worker_service import get_worker_service as get_service
    return get_service(db)

@router.get("/status")
def get_chaos_status(db: Session = Depends(get_db), worker_service: WorkerService = Depends(get_worker_service)):
    # api health
    # leader info
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    leader_id = redis_client.get("scheduler:leader")
    
    # worker info
    active_workers = worker_service.list_active_workers(0, 1000)
    dead_workers = worker_service.list_dead_workers(0, 1000)
    
    # job counts
    total_jobs = db.query(Job).count()
    pending_jobs = db.query(Job).filter(Job.status == JobStatus.PENDING).count()
    running_jobs = db.query(Job).filter(Job.status == JobStatus.RUNNING).count()
    failed_jobs = db.query(Job).filter(Job.status == JobStatus.FAILED).count()
    completed_jobs = db.query(Job).filter(Job.status == JobStatus.SUCCESS).count()
    dead_letter_jobs = db.query(Job).filter(Job.status == JobStatus.DEAD_LETTER).count()
    
    # schedule counts
    total_schedules = db.query(Schedule).count()
    
    return {
        "api_health": "ok",
        "leader": {
            "leader_id": leader_id,
            "status": "active" if leader_id else "no_leader"
        },
        "workers": {
            "total": len(active_workers) + len(dead_workers),
            "active": len(active_workers),
            "dead": len(dead_workers),
            "active_list": [w.worker_id for w in active_workers],
            "dead_list": [w.worker_id for w in dead_workers]
        },
        "jobs": {
            "total": total_jobs,
            "pending": pending_jobs,
            "running": running_jobs,
            "failed": failed_jobs,
            "success": completed_jobs,
            "dead_letter": dead_letter_jobs
        },
        "schedules": {
            "total": total_schedules
        }
    }
