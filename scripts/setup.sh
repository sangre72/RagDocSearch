#!/bin/bash

set -e

echo "=== RAG Document Search 설정 ==="

# 1. PostgreSQL 데이터베이스 생성
echo "[1/4] PostgreSQL 데이터베이스 설정..."
psql postgres -c "CREATE DATABASE ragdoc;" 2>/dev/null || echo "  - 데이터베이스가 이미 존재합니다"
psql ragdoc -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null
echo "  - pgvector 확장 활성화 완료"

# 2. Backend 설정
echo "[2/4] Backend 설정..."
cd "$(dirname "$0")/../backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  - 가상환경 생성 완료"
fi
source venv/bin/activate
pip install -r requirements.txt -q
echo "  - 의존성 설치 완료"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  - .env 파일 생성됨 (OpenAI API 키를 설정해주세요)"
fi

# 3. Frontend 설정
echo "[3/4] Frontend 설정..."
cd ../frontend
npm install -q
if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local
    echo "  - .env.local 파일 생성됨"
fi
echo "  - 의존성 설치 완료"

echo ""
echo "=== 설정 완료! ==="
echo ""
echo "시작하려면:"
echo "1. backend/.env 파일에 OPENAI_API_KEY를 설정하세요"
echo "2. ./scripts/start.sh 를 실행하세요"
