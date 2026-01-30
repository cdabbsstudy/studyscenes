from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import projects, generation

app = FastAPI(title="StudyScenes", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(generation.router)

# Serve generated files
storage_dir = settings.storage_dir
app.mount("/storage", StaticFiles(directory=str(storage_dir)), name="storage")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
