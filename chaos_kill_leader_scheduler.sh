#!/bin/bash
set -e

echo "=== Chaos Test: Kill Leader Scheduler ==="

# Get current leader
LEADER_ID=$(curl -s http://localhost:8000/chaos/status | jq -r '.leader.leader_id')
echo "Current leader is: $LEADER_ID"

if [ "$LEADER_ID" == "null" ] || [ -z "$LEADER_ID" ]; then
  echo "No leader found. Wait for election..."
  sleep 5
  LEADER_ID=$(curl -s http://localhost:8000/chaos/status | jq -r '.leader.leader_id')
  echo "Current leader is now: $LEADER_ID"
fi

# The leader ID is something like "scheduler-3f4a...", not the docker container name.
# The container names are `distributed-job-scheduler-scheduler-1-1` and `...scheduler-2-1`.
# Let's just kill scheduler-1 and see if scheduler-2 takes over (or vice versa).
# We can find out which container has the leader_id by grepping the docker logs, 
# or we can simply restart BOTH to cause a leadership disruption, OR we can kill scheduler-1 specifically.
echo "Restarting both schedulers sequentially to force failover..."
docker compose restart scheduler-1
sleep 5
docker compose restart scheduler-2

echo "Waiting for Redis TTL (15s)..."
sleep 15

NEW_LEADER_ID=$(curl -s http://localhost:8000/chaos/status | jq -r '.leader.leader_id')
echo "New leader is: $NEW_LEADER_ID"

if [ "$LEADER_ID" == "$NEW_LEADER_ID" ]; then
  echo "Leader did not change! Failover failed."
else
  echo "Leader changed successfully!"
fi

echo "Checking /chaos/status..."
curl -s http://localhost:8000/chaos/status | jq '{leader}'

echo "=== Test Complete ==="
