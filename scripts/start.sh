#!/bin/bash

set -e

SCRIPT_DIR="$(dirname "$0")"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== RAG Document Search 시작 ==="

# Backend 시작
echo "[Backend] 시작 중... (http://localhost:8000)"
cd "$PROJECT_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend 시작
echo "[Frontend] 시작 중... (http://localhost:3000)"
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=== 서비스 시작됨 ==="
echo "- Backend:  http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"

# 종료 시 정리
cleanup() {
    echo ""
    echo "서비스 종료 중..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# 대기
wait
