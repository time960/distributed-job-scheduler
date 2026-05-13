#!/bin/bash

echo "🚀 Starting Distributed Job Scheduler Load Testing Environment..."
docker compose down -v --remove-orphans
docker compose up --build -d

echo ""
echo "✅ Environment is up!"
echo ""
echo "To start the load test, open the Locust UI:"
echo "👉 http://localhost:8089"
echo ""
echo "For a Headless test (100 users, 10 spawn rate, 1 min), run:"
echo "docker compose exec locust locust -f /mnt/locust/locustfile.py --host http://api:8000 --headless -u 100 -r 10 --run-time 1m"
echo ""
echo "Watch the system metrics in Grafana:"
echo "👉 http://localhost:3000 (admin/admin)"
