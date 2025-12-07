#!/usr/bin/env bash
set -e

# Prefer Python 3.12 via py on Windows; fall back to python3 on Linux/mac
if command -v py >/dev/null 2>&1; then
  PY_CMD="py -3.12"
else
  PY_CMD="python3"
fi

# 1. Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
  $PY_CMD -m venv .venv
fi

# 2. Activate the virtual environment
if [ -f ".venv/Scripts/activate" ]; then
  # Windows (Git Bash)
  source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
  # Linux/mac
  source .venv/bin/activate
else
  echo "Could not find virtual environment activation script."
  exit 1
fi

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Install Playwright browsers
python -m playwright install || true

# 5. Start the FastAPI server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
