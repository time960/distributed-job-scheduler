#!/bin/bash
set -e

echo "=== Chaos Test: Kill Worker ==="
echo "Creating 5 long-running jobs..."
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/jobs \
    -H "Content-Type: application/json" \
    -d '{"name": "long_job_'"$i"'", "payload": {"sleep": 10}, "priority": 1, "max_attempts": 3}' > /dev/null
done

echo "Waiting for worker to pick up jobs (3s)..."
sleep 3

echo "Killing worker container..."
docker compose kill worker

echo "Waiting 5 seconds..."
sleep 5

echo "Starting worker container..."
docker compose start worker

echo "Waiting for recovery and processing (75s for 60s timeout)..."
sleep 75

echo "Checking /chaos/status..."
curl -s http://localhost:8000/chaos/status | jq '{jobs}'

echo "=== Test Complete ==="
