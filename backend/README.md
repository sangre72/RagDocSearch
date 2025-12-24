# RAG Document Search - 백엔드

FastAPI 기반의 RAG 문서 검색 백엔드 서버입니다.

## 기술 스택

- **Python 3.10+** - 런타임
- **FastAPI** - 웹 프레임워크
- **LangChain** - RAG 파이프라인
- **PostgreSQL + pgvector** - 벡터 데이터베이스
- **OpenAI** - 임베딩 및 LLM
- **SQLAlchemy** - ORM

## 프로젝트 구조

```
app/
├── main.py           # FastAPI 앱 진입점
├── config.py         # 환경 설정
├── database.py       # PostgreSQL 연결
├── models.py         # SQLAlchemy 모델
├── schemas.py        # Pydantic 스키마
├── routers/          # API 라우터
│   ├── documents.py  # 문서 업로드/관리
│   └── search.py     # 검색/채팅
└── services/         # 비즈니스 로직
    ├── pdf_service.py   # PDF 처리
    └── rag_service.py   # RAG 검색
```

## 설치

### uv 사용 (권장)

[uv](https://github.com/astral-sh/uv)는 빠른 Python 패키지 관리 도구입니다.

```bash
# uv 설치 (미설치 시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성
uv venv

# 가상환경 활성화
source .venv/bin/activate

# 의존성 설치
uv pip install -r requirements.txt
```

### pip 사용 (대안)

```bash
# 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 환경 변수 설정

`.env` 파일을 생성하고 다음 변수를 설정합니다:

```env
# OpenAI API 키 (필수)
OPENAI_API_KEY=your-openai-api-key

# PostgreSQL 데이터베이스 연결 URL
DATABASE_URL=postgresql://localhost:5432/ragdoc
```

## 데이터베이스 설정

```bash
# PostgreSQL 데이터베이스 생성
psql postgres -c "CREATE DATABASE ragdoc;"

# pgvector 확장 활성화
psql ragdoc -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 개발 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 문서 관리

| 메서드 | 엔드포인트 | 설명 |
|--------|----------|-------------|
| POST | `/api/documents/upload` | PDF 업로드 |
| GET | `/api/documents` | 문서 목록 조회 |
| GET | `/api/documents/{id}` | 문서 상세 조회 |
| DELETE | `/api/documents/{id}` | 문서 삭제 |

### 검색

| 메서드 | 엔드포인트 | 설명 |
|--------|----------|-------------|
| POST | `/api/search` | 벡터 검색 |
| POST | `/api/search/chat` | RAG 채팅 |

## 주요 기능

1. **PDF 처리** - PDF 업로드, 텍스트 추출, 청크 분할
2. **벡터 임베딩** - OpenAI 임베딩으로 문서 벡터화
3. **유사도 검색** - pgvector 코사인 유사도 검색
4. **RAG 채팅** - 문서 컨텍스트 기반 AI 응답 생성
