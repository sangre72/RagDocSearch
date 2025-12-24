# RAG Document Search - 프론트엔드

Next.js 15 기반의 RAG 문서 검색 프론트엔드입니다.

## 기술 스택

- **Next.js 15** - React 프레임워크
- **React 19** - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **Axios** - HTTP 클라이언트
- **Lucide React** - 아이콘

## 프로젝트 구조

```
src/
├── app/                # Next.js App Router
│   ├── layout.tsx     # 루트 레이아웃
│   └── page.tsx       # 메인 페이지
├── components/        # React 컴포넌트
│   ├── ChatInterface.tsx    # 채팅 UI
│   ├── DocumentList.tsx     # 문서 목록
│   └── DocumentUpload.tsx   # 파일 업로드
├── lib/               # 유틸리티
│   └── api.ts         # API 클라이언트
└── types/             # TypeScript 타입
    ├── document.ts    # 문서 관련 타입
    ├── search.ts      # 검색 관련 타입
    └── index.ts       # 타입 re-export
```

## 개발 서버 실행

```bash
npm run dev
```

[http://localhost:3000](http://localhost:3000)에서 확인할 수 있습니다.

## 빌드

```bash
npm run build
```

## 환경 변수

`.env.local` 파일을 생성하고 다음 변수를 설정합니다:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 주요 기능

1. **문서 업로드** - 드래그 앤 드롭으로 PDF 업로드
2. **문서 관리** - 업로드된 문서 목록 조회 및 삭제
3. **문서 선택** - 검색 대상 문서 선택
4. **RAG 채팅** - 문서 기반 AI 질의응답
