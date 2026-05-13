# Interview Guide: System Design Concepts

This document contains deep-dive explanations of the system design choices made in this project. Use this to confidently answer technical questions during engineering interviews.

---

### 1. Why didn't you just use Celery or RabbitMQ?
* **Answer**: "While Celery and RabbitMQ are industry standards, my goal was to deeply understand the underlying mechanics of distributed queues. By building this from scratch using PostgreSQL and Redis, I could demonstrate my grasp of atomic database locks (`SKIP LOCKED`), leader election algorithms, exponential backoff, and state recovery. It allowed me to handle race conditions explicitly rather than relying on a black-box framework."

### 2. How do you prevent two workers from picking up the exact same job?
* **Answer**: "I used PostgreSQL's `SELECT FOR UPDATE SKIP LOCKED` capability. When a worker queries for pending jobs, `FOR UPDATE` places a row-level lock on the retrieved records. `SKIP LOCKED` ensures that if a second worker queries the table at the exact same millisecond, it simply skips the rows locked by the first worker and grabs the next available jobs. This entirely eliminates duplicate processing without blocking the database or causing lock contention delays."

### 3. What happens if a worker container crashes while it is processing a job?
* **Answer**: "The system implements a heartbeat and liveness tracker. When a worker starts a job, it updates the job's status to `RUNNING` and sets a `locked_at` timestamp. If the worker crashes, it won't be able to mark the job as `SUCCESS`. A sweeper function periodically scans the database for `RUNNING` jobs where the `locked_at` timestamp is older than the configured `job_timeout_seconds`. These abandoned jobs are safely swept back to the `PENDING` queue to be picked up by a healthy worker."

### 4. How does the Cron Scheduler work across multiple nodes without duplicating schedules?
* **Answer**: "To make the scheduler highly available, I deploy multiple replicas (`scheduler-1`, `scheduler-2`). To prevent them from both scheduling the same cron job at the same time, I implemented a **Leader Election** pattern using a Redis distributed lock. 
    1. Instances race to set a `scheduler:leader` key with a short Time-To-Live (TTL).
    2. Only the instance that acquires the lock acts as the leader and dispatches jobs.
    3. The leader continuously renews the TTL heartbeat. 
    4. If the leader crashes, the TTL expires, and the follower instantly grabs the lock and takes over."

### 5. Even with Leader Election, what if there's a split-brain or network delay? How do you guarantee idempotency?
* **Answer**: "As a final safeguard, the database enforces a unique constraint (`uq_job_schedule_time`) on the combination of `schedule_id` and `scheduled_for` timestamp. Even if two schedulers somehow bypass the Redis lock and attempt to create a job for the same cron tick simultaneously, the database will reject the duplicate transaction. The architecture guarantees idempotency at the lowest possible data layer."

### 6. Explain your Retry Logic and Dead Letter Queue (DLQ).
* **Answer**: "Network requests and third-party APIs fail. If a job throws an exception, it isn't discarded. The system checks the `max_attempts` configured for that job. If retries remain, it calculates a `next_retry_at` timestamp using **exponential backoff** (e.g., waiting 2s, then 4s, then 8s) combined with **random jitter** to prevent a 'thundering herd' of synchronized retries hitting a recovering downstream service. If the job exhausts all attempts, it is permanently marked as `DEAD_LETTER` so an engineer can manually inspect the payload and error logs."

### 7. How did you prove the system is actually fault-tolerant?
* **Answer**: "I built a Chaos Engineering suite (`test_chaos.sh`) using Bash and Docker Compose. I simulated real-world disasters:
    1. **Worker Crashes**: Killed containers mid-processing and verified the timeout sweeper recovered 100% of jobs.
    2. **Database Outages**: Restarted the PostgreSQL container under load and verified that the SQLAlchemy connection pool successfully re-established connections without permanently hanging the API.
    3. **Retry Storms**: Injected massive amounts of failing payloads and verified the DLQ absorbed them correctly without crashing the worker pool.
    4. **Performance load testing**: Used Locust to swarm the API, optimizing database queries to achieve >500 jobs/sec with a verified 0% failure rate."
