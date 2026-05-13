#!/bin/bash
set -e

echo "========================================="
echo "   VERSION 9: CHAOS TESTING RUNNER       "
echo "========================================="

echo "[1/4] Running Worker Chaos Test..."
./chaos_kill_worker.sh
echo ""

echo "[2/4] Running Leader Scheduler Chaos Test..."
./chaos_kill_leader_scheduler.sh
echo ""

echo "[3/4] Running PostgreSQL Restart Chaos Test..."
./chaos_restart_postgres.sh
echo ""

echo "[4/4] Running Retry Storm Chaos Test..."
./chaos_retry_storm.sh
echo ""

echo "========================================="
echo "   ALL CHAOS TESTS COMPLETED             "
echo "========================================="
