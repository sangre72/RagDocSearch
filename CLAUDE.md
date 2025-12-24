# CLAUDE.md - RagDocSearch 프로젝트 가이드

이 파일은 Claude Code가 프로젝트를 이해하고 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

PDF 문서를 업로드하고 RAG (Retrieval-Augmented Generation) 기반으로 검색하는 시스템

### 기술 스택
- **Backend**: Python 3.10+, FastAPI, LangChain, pgvector
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 17 + pgvector

## 아키텍처 가이드

### 디렉토리 구조

```
RagDocSearch/
├── backend/                 # Python FastAPI 서버
│   └── app/
│       ├── main.py         # FastAPI 앱 진입점
│       ├── config.py       # 환경 설정
│       ├── database.py     # PostgreSQL 연결
│       ├── models.py       # SQLAlchemy 모델
│       ├── schemas.py      # Pydantic 스키마 (API 타입)
│       ├── routers/        # API 라우터
│       │   ├── documents.py
│       │   └── search.py
│       └── services/       # 비즈니스 로직
│           ├── pdf_service.py
│           └── rag_service.py
├── frontend/               # Next.js 앱
│   └── src/
│       ├── app/           # Next.js App Router
│       ├── components/    # React 컴포넌트
│       ├── lib/           # API 클라이언트, 유틸리티
│       └── types/         # TypeScript 타입 정의
└── scripts/               # 실행 스크립트
```

### 모듈화 원칙

#### 1. 타입 정의 규칙

**Backend (Python)**
- 모든 API 스키마는 `app/schemas.py`에 정의
- DB 모델은 `app/models.py`에 정의
- Pydantic을 사용하여 타입 안전성 보장

**Frontend (TypeScript)**
- 공유 타입은 `src/types/`에 도메인별 분리
  - `document.ts` - 문서 관련 타입
  - `search.ts` - 검색 관련 타입
  - `index.ts` - Public API (re-export)
- 컴포넌트 내부 타입은 해당 파일에 정의
- `import type` 구문 사용 (런타임 의존성 제거)

#### 2. 레이어 분리

```
Frontend:
  types/      → 타입 정의 (순수)
  lib/        → API 클라이언트, 유틸리티
  components/ → UI 컴포넌트
  app/        → 페이지, 라우팅

Backend:
  schemas.py  → API 타입 정의
  models.py   → DB 모델
  services/   → 비즈니스 로직
  routers/    → HTTP 엔드포인트
```

#### 3. 의존성 방향

```
types/ (최하위) ← lib/ ← components/ ← app/ (최상위)
```

- 상위 레이어만 하위 레이어 import 가능
- 순환 의존성 금지

### Backend/Frontend 스키마 동기화

| Backend (schemas.py) | Frontend (types/) |
|---------------------|-------------------|
| DocumentResponse | Document |
| DocumentListResponse | DocumentListResponse |
| UploadResponse | UploadResponse |
| SearchQuery | SearchQuery |
| SearchResult | SearchResult |
| SearchResponse | SearchResponse |
| ChatQuery | ChatQuery |
| ChatResponse | ChatResponse |

## 개발 가이드

### 환경 설정

1. Backend `.env` 필수 설정:
   - `OPENAI_API_KEY` (필수)
   - `DATABASE_URL` (기본: postgresql://localhost:5432/ragdoc)

2. Frontend `.env.local`:
   - `NEXT_PUBLIC_API_URL` (기본: http://localhost:8000/api)

### 실행 방법

```bash
# 초기 설정
./scripts/setup.sh

# 서비스 시작
./scripts/start.sh
```

### API 엔드포인트

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/documents/upload | PDF 업로드 |
| GET | /api/documents | 문서 목록 |
| DELETE | /api/documents/{id} | 문서 삭제 |
| POST | /api/search | 벡터 검색 |
| POST | /api/search/chat | RAG 채팅 |

## 리팩터링 TODO

- [ ] Backend 테스트 코드 추가
- [ ] Frontend 테스트 코드 추가
- [ ] Error handling 개선
- [ ] Loading states 개선
- [ ] 문서 미리보기 기능

## 코드 스타일

### Python
- Black 포맷터 사용
- Type hints 필수
- Docstring 작성 권장

### TypeScript
- ESLint + Prettier
- `import type` 사용
- 컴포넌트는 함수형 + hooks
