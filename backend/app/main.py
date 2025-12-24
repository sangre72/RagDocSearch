from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import documents, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title="RAG Document Search API",
    description="PDF 문서를 업로드하고 RAG 기반 검색을 수행하는 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api")
app.include_router(search.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "RAG Document Search API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
