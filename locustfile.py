import random
import uuid
from locust import HttpUser, task, between

class SchedulerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # We can store some job IDs created by this user to query them later
        self.created_job_ids = []

    @task(4)
    def create_normal_job(self):
        payload = {
            "name": f"load_test_job_{uuid.uuid4().hex[:8]}",
            "payload": {"type": "normal", "data": "test"},
            "priority": random.randint(0, 5),
            "max_attempts": 3
        }
        with self.client.post("/jobs", json=payload, catch_response=True) as response:
            if response.status_code in [200, 201]:
                try:
                    job_id = response.json().get("id")
                    if job_id:
                        self.created_job_ids.append(job_id)
                    response.success()
                except Exception as e:
                    response.failure(f"Failed to parse JSON: {e}")
            else:
                response.failure(f"Failed to create job: {response.status_code} {response.text}")

    @task(1)
    def create_high_priority_job(self):
        payload = {
            "name": f"high_priority_{uuid.uuid4().hex[:8]}",
            "payload": {"type": "urgent", "data": "test"},
            "priority": 10,
            "max_attempts": 3
        }
        self.client.post("/jobs", json=payload)

    @task(1)
    def create_failing_job(self):
        payload = {
            "name": f"failing_job_{uuid.uuid4().hex[:8]}",
            "payload": {"should_fail": True, "data": "test"},
            "priority": 0,
            "max_attempts": 2
        }
        self.client.post("/jobs", json=payload)

    @task(2)
    def create_scheduled_job(self):
        payload = {
            "name": f"cron_job_{uuid.uuid4().hex[:8]}",
            "cron_expression": "*/5 * * * *",
            "payload": {"type": "scheduled"},
            "priority": 5,
            "max_attempts": 3
        }
        self.client.post("/schedules", json=payload)

    @task(3)
    def read_jobs(self):
        # Query with some filters to simulate dashboard traffic
        status_filter = random.choice(["pending", "running", "success", "failed", ""])
        url = "/jobs?limit=50"
        if status_filter:
            url += f"&status={status_filter}"
        self.client.get(url)

    @task(3)
    def read_single_job(self):
        if self.created_job_ids:
            job_id = random.choice(self.created_job_ids)
            self.client.get(f"/jobs/{job_id}", name="/jobs/{job_id}")
            
            # Keep list manageable
            if len(self.created_job_ids) > 100:
                self.created_job_ids = self.created_job_ids[-50:]

    @task(1)
    def read_metrics(self):
        self.client.get("/metrics")
