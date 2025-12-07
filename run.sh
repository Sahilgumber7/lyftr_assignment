#!/usr/bin/env bash
set -e

# Prefer Python 3.12 via py on Windows; fall back to python3 on Linux/mac
if command -v py >/dev/null 2>&1; then
  PY_CMD="py -3.12"
else
  PY_CMD="python3"
fi

BACKEND_PORT=${BACKEND_PORT:-8000}   # default but overridable
FRONTEND_PORT=""                    # we'll auto-detect this later

# 1. Create venv if needed
if [ ! -d ".venv" ]; then
  $PY_CMD -m venv .venv
fi

# 2. Activate venv
if [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "Could not find virtual environment activation script."
  exit 1
fi

echo "Backend environment ready."

# 3. Install backend dependencies
python -m pip install -r requirements.txt

# 4. Install Playwright
python -m playwright install || true

# 5. Start backend (in background)
echo "Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!

echo "Backend started on port $BACKEND_PORT"

# 6. Start frontend
echo "Starting React frontend..."
cd scraper-frontend
npm install

# Capture frontend logs and detect port dynamically
npm start 2>&1 | tee frontend.log &
FRONTEND_PID=$!
cd ..

# Wait until React logs the port (3000/3001/etc.)
echo "Waiting for frontend to report its port..."

while [ -z "$FRONTEND_PORT" ]; do
  if grep -q "Local:" scraper-frontend/frontend.log; then
    FRONTEND_PORT=$(grep "Local:" scraper-frontend/frontend.log | head -1 | sed 's/.*http:\/\/localhost://')
  fi
  sleep 1
done

echo ""
echo "=========================================="
echo "Both servers are now running:"
echo ""
echo "Frontend: http://localhost:${FRONTEND_PORT}"
echo "Backend API: http://localhost:${BACKEND_PORT}"
echo "Backend Docs: http://localhost:${BACKEND_PORT}/docs"
echo ""
echo "Press CTRL+C to stop everything."
echo "=========================================="
echo ""

wait
