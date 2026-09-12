#!/usr/bin/env bash
# Starts the 3 mock agents + the orchestrator together for local testing.
# Run this from the foodwise-ai/ project root:
#   bash orchestrator/run_local_dev.sh
#
# Stop everything with Ctrl+C.

set -e

echo "Starting mock query_agent on :8001 ..."
uvicorn orchestrator.mocks.mock_query_agent:app --port 8001 &
PID1=$!

echo "Starting mock retrieval_agent on :8002 ..."
uvicorn orchestrator.mocks.mock_retrieval_agent:app --port 8002 &
PID2=$!

echo "Starting mock review_agent on :8003 ..."
uvicorn orchestrator.mocks.mock_review_agent:app --port 8003 &
PID3=$!

sleep 1

echo "Starting orchestrator on :8000 ..."
uvicorn orchestrator.main:app --reload --port 8000 &
PID4=$!

trap "echo 'Stopping...'; kill $PID1 $PID2 $PID3 $PID4" EXIT INT TERM

wait
