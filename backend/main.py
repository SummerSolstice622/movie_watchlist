"""
Movie Tracker API - 独立电影追踪后端
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .tmdb_client import TMDBClient
from .cinema_router import router as cinema_router
from .movie_admin_router import router as movie_admin_router
from .movie_router import router as movie_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    yield
    await TMDBClient.close_global()


app = FastAPI(
    title="Movie Tracker API",
    description="电影观看记录追踪后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movie_router)
app.include_router(movie_admin_router)
app.include_router(cinema_router)


@app.get("/api/health")
def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5002)
