#!/bin/bash
set -e

echo "=== Chaos Test: Retry Storm ==="
echo "Creating 50 failing jobs..."
for i in {1..50}; do
  curl -s -X POST http://localhost:8000/jobs \
    -H "Content-Type: application/json" \
    -d '{"name": "failing_job_'"$i"'", "payload": {"should_fail": true}, "priority": 5, "max_attempts": 3}' > /dev/null
done

echo "Jobs created. Monitoring /chaos/status..."
echo "Workers will retry these jobs 3 times with exponential backoff."

for i in {1..15}; do
  echo "--- Check $i/15 ---"
  curl -s http://localhost:8000/chaos/status | jq '{jobs}'
  sleep 5
done

echo "=== Test Complete ==="
