# Resume Bullets: Distributed Job Scheduler

*Copy and paste the bullets below that best fit the role you are applying for. They are written using the STAR method and optimized for ATS systems.*

### Backend / Distributed Systems Engineer Role
- **Architected and developed a distributed job scheduling engine** using Python, FastAPI, and PostgreSQL, orchestrating asynchronous workloads across multiple worker nodes to achieve >500 jobs/sec throughput.
- **Engineered a deadlock-free concurrent queue** by leveraging PostgreSQL `SELECT FOR UPDATE SKIP LOCKED` combined with SQLAlchemy, completely eliminating the need for complex external brokers while guaranteeing exactly-once processing.
- **Implemented high-availability distributed cron scheduling** using Redis-backed Leader Election; successfully eliminated duplicate execution race conditions and achieved <10 second automated failover during node crashes.
- **Designed an exponential backoff retry system** with algorithmic jitter, routing persistently failing transactions to a Dead Letter Queue (DLQ) to prevent systemic "retry storms."

### DevOps / SRE / Platform Engineer Role
- **Built an automated chaos engineering suite** using Bash and Docker Compose to simulate hard container crashes, database disconnections, and retry storms, verifying 100% data preservation and fault-tolerant system recovery.
- **Deployed a comprehensive observability stack** integrating custom Prometheus middleware and Grafana dashboards to track critical SLIs including active worker pools, DLQ backlogs, and API p99 latencies under load.
- **Executed high-concurrency performance benchmarking** utilizing Locust, optimizing database connection pooling and query efficiency to maintain a 0% HTTP failure rate at peak throughput.
- **Containerized a multi-service architecture** (API, Schedulers, Workers, Redis, DB, Metrics) using Docker, streamlining local development environments and CI/CD readiness.

### Python Software Engineer Role
- **Built a high-performance RESTful API** using FastAPI and Pydantic for rigorous data validation, enabling strict schema compliance for distributed scheduling payloads.
- **Streamlined database interactions** via synchronous SQLAlchemy ORM, designing complex recursive data models and utilizing Alembic for seamless, version-controlled schema migrations.
- **Created a modular, interview-ready Python codebase** enforcing strict typing, dependency injection, and clean separation of concerns across service, repository, and presentation layers.
