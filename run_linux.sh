#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

MODE="dev"
if [ "${CARTOPHARMA_MODE:-}" = "docker" ]; then
  MODE="docker"
fi

for arg in "$@"; do
  case "$arg" in
    --docker)
      MODE="docker"
      ;;
    --dev)
      MODE="dev"
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      echo "Usage: ./run_linux.sh [--dev|--docker]" >&2
      exit 1
      ;;
  esac
done

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  echo "Python is not installed." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js/npm is not installed." >&2
  exit 1
fi

API_PID=""
cleanup() {
  if [ -n "${API_PID}" ] && kill -0 "${API_PID}" >/dev/null 2>&1; then
    kill "${API_PID}" >/dev/null 2>&1 || true
    wait "${API_PID}" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

wait_for_backend_health() {
  "$PYTHON_BIN" - <<'PY'
import sys
import time
import urllib.request

url = "http://127.0.0.1:8000/health"
deadline = time.time() + 45.0
while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=2.0) as response:
            if response.status == 200:
                sys.exit(0)
    except Exception:
        pass
    time.sleep(0.5)
sys.exit(1)
PY
}

if [ "$MODE" = "docker" ]; then
  echo "[INFO] Running CartoPharma in docker mode"
  (
    cd backend
    "$PYTHON_BIN" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  ) &
  API_PID=$!

  wait_for_backend_health
  cd frontend
  npm run start -- -H 0.0.0.0 -p 3000
  exit 0
fi

if [ ! -f ".venv/bin/activate" ]; then
  rm -rf .venv
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

(
  cd backend
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &
API_PID=$!

cd frontend
if [ ! -d "node_modules" ]; then
  if [ -f "package-lock.json" ]; then
    npm ci
  else
    npm install
  fi
fi

npm run dev
