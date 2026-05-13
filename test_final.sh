#!/bin/bash
set -e

echo "========================================="
echo "   DISTRIBUTED SCHEDULER SMOKE TEST      "
echo "========================================="

echo "\n--- 1. Checking API Health ---"
curl -s -f http://localhost:8000/health | jq

echo "\n--- 2. Checking Leader Election ---"
curl -s -f http://localhost:8000/leader | jq

echo "\n--- 3. Checking Active Workers ---"
curl -s -f http://localhost:8000/workers/active | jq

echo "\n--- 4. Submitting a Job ---"
curl -s -f -X POST "http://localhost:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{"name":"smoke_test_job","payload":{"test": true},"priority":1}' | jq

echo "\nWaiting 5s for worker to process..."
sleep 5

echo "\n--- 5. Checking Jobs List ---"
curl -s -f http://localhost:8000/jobs | jq '.[:3]'

echo "\n--- 6. Checking Metrics (Prometheus Format) ---"
curl -s -f http://localhost:8000/metrics | head -n 10

echo "\n--- 7. Checking Chaos Observability Status ---"
curl -s -f http://localhost:8000/chaos/status | jq

echo "\n========================================="
echo "   ALL SMOKE TESTS PASSED SUCCESSFULLY!  "
echo "========================================="
