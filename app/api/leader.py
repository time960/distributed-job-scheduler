from fastapi import APIRouter
import redis
from app.config import settings

router = APIRouter()

@router.get("")
def get_leader():
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    leader_id = redis_client.get("scheduler:leader")
    ttl = redis_client.ttl("scheduler:leader")
    
    return {
        "leader_id": leader_id,
        "ttl": ttl if ttl > 0 else None,
        "status": "active" if leader_id else "no_leader"
    }
