from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import jobs, schedules, workers, leader, metrics, chaos
import time
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('api_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('api_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])

app = FastAPI(title="Distributed Job Scheduler")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Do not track latency for /metrics itself to avoid noise
    if request.url.path != "/metrics":
        REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
        
    return response

app.include_router(jobs.router)
app.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])
app.include_router(workers.router, prefix="/workers", tags=["Workers"])
app.include_router(leader.router, prefix="/leader", tags=["Leader Election"])
app.include_router(metrics.router)
app.include_router(chaos.router, prefix="/chaos", tags=["Chaos Testing"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
