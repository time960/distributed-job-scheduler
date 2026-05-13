#!/bin/bash
set -e

echo "=== Chaos Test: Restart PostgreSQL ==="
echo "Creating a job before restart..."
curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"name": "pre_db_restart", "payload": {"data": "test"}, "priority": 1, "max_attempts": 3}' > /dev/null

echo "Restarting PostgreSQL container..."
docker compose restart postgres

echo "Waiting for PostgreSQL to recover (10s)..."
sleep 10

echo "Creating a job after restart..."
curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"name": "post_db_restart", "payload": {"data": "test"}, "priority": 1, "max_attempts": 3}' > /dev/null

echo "Waiting for workers to process jobs (5s)..."
sleep 5

echo "Checking /chaos/status..."
curl -s http://localhost:8000/chaos/status | jq '{jobs, api_health}'

echo "=== Test Complete ==="
