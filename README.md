# RAG Document Search

PDF 문서를 업로드하고 AI 기반으로 검색하는 RAG (Retrieval-Augmented Generation) 시스템입니다.

## 기술 스택

### 백엔드
- **Python 3.10+** - FastAPI 웹 프레임워크
- **LangChain** - RAG 파이프라인
- **PostgreSQL 17 + pgvector** - 벡터 데이터베이스
- **OpenAI** - 임베딩 및 LLM

### 프론트엔드
- **Next.js 15** (React 19)
- **TypeScript**
- **Tailwind CSS**

## 프로젝트 구조

```
RagDocSearch/
├── backend/                      # 백엔드 (Python)
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 진입점
│   │   ├── config.py            # 환경 설정
│   │   ├── database.py          # PostgreSQL 연결
│   │   ├── models.py            # SQLAlchemy 모델
│   │   ├── schemas.py           # Pydantic 스키마
│   │   ├── routers/             # API 라우터
│   │   │   ├── documents.py     # 문서 업로드/관리
│   │   │   └── search.py        # 검색/채팅
│   │   └── services/            # 비즈니스 로직
│   │       ├── pdf_service.py   # PDF 처리
│   │       └── rag_service.py   # RAG 검색
│   ├── requirements.txt
│   └── .env.example
├── frontend/                     # 프론트엔드 (Next.js)
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   ├── components/          # React 컴포넌트
│   │   ├── lib/                 # API 클라이언트
│   │   └── types/               # TypeScript 타입 정의
│   └── package.json
└── scripts/                      # 실행 스크립트
    ├── setup.sh                 # 초기 설정
    └── start.sh                 # 서비스 시작
```

## 설치 및 실행

### 사전 요구사항

- Python 3.10+
- Node.js 20+
- PostgreSQL 17+ (pgvector 확장)
- OpenAI API Key
- [uv](https://github.com/astral-sh/uv) (권장) 또는 pip

### 1. 초기 설정

```bash
./scripts/setup.sh
```

### 2. OpenAI API 키 설정

`backend/.env` 파일을 편집하여 OpenAI API 키를 설정합니다:

```env
OPENAI_API_KEY=your-api-key-here
```

### 3. 서비스 시작

```bash
./scripts/start.sh
```

또는 개별 실행:

```bash
# Backend (uv 사용)
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (새 터미널)
cd frontend
npm install
npm run dev
```

### 4. 접속

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

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

1. **PDF 업로드**: 드래그 앤 드롭으로 PDF 문서 업로드
2. **자동 벡터화**: 문서 내용을 자동으로 청크 분할 및 임베딩
3. **의미 기반 검색**: pgvector를 활용한 유사도 검색
4. **RAG 채팅**: 문서 내용 기반 AI 질의응답
5. **문서 선택 검색**: 특정 문서만 선택하여 검색 가능

## 환경 변수

### 백엔드 (.env)

| 변수명 | 설명 | 기본값 |
|------|------|--------|
| OPENAI_API_KEY | OpenAI API 키 | (필수) |
| DATABASE_URL | PostgreSQL 연결 URL | postgresql://localhost:5432/ragdoc |
| EMBEDDING_MODEL | 임베딩 모델 | text-embedding-3-small |
| LLM_MODEL | LLM 모델 | gpt-4o-mini |
| MAX_FILE_SIZE | 최대 파일 크기 | 10485760 (10MB) |

### 프론트엔드 (.env.local)

| 변수명 | 설명 | 기본값 |
|------|------|--------|
| NEXT_PUBLIC_API_URL | 백엔드 API URL | http://localhost:8000/api |
