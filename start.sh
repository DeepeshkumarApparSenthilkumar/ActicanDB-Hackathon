#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Actian VectorAI DB..."
cd "$SCRIPT_DIR"
docker compose up -d
echo "Waiting for VectorAI DB to be ready on :50051..."
until docker compose exec vectoraidb echo ok 2>/dev/null; do sleep 1; done

echo "Starting RepoMind backend..."
cd "$SCRIPT_DIR/backend" && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting RepoMind frontend..."
cd "$SCRIPT_DIR/frontend" && npm run dev &
FRONTEND_PID=$!

echo ""
echo "  VectorAI DB: localhost:50051 (gRPC)"
echo "  Backend:     http://localhost:8000"
echo "  Frontend:    http://localhost:5173"
echo "  API docs:    http://localhost:8000/docs"
echo ""

trap "docker compose -f '$SCRIPT_DIR/docker-compose.yml' down; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait $BACKEND_PID $FRONTEND_PID
