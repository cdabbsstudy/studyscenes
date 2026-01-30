from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.generation import (
    OutlineResponse,
    OutlineUpdate,
    ScriptResponse,
    ScriptUpdate,
    AssetStatusResponse,
    VideoStatusResponse,
)
from app.services import pipeline

router = APIRouter(prefix="/api/projects", tags=["generation"])


@router.post("/{project_id}/generate/outline", response_model=OutlineResponse)
async def generate_outline(project_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await pipeline.generate_outline(project_id, db)
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.put("/{project_id}/outline", response_model=OutlineResponse)
async def save_outline(project_id: str, data: OutlineUpdate, db: AsyncSession = Depends(get_db)):
    try:
        outline = OutlineResponse(sections=data.sections)
        await pipeline.save_outline(project_id, outline, db)
        return outline
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{project_id}/generate/script", response_model=ScriptResponse)
async def generate_script(project_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await pipeline.generate_script(project_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{project_id}/script", response_model=ScriptResponse)
async def save_script(project_id: str, data: ScriptUpdate, db: AsyncSession = Depends(get_db)):
    try:
        script = ScriptResponse(scenes=data.scenes)
        await pipeline.save_script(project_id, script, db)
        return script
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{project_id}/generate/assets")
async def generate_assets(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Verify project exists before starting background task
    try:
        project = await pipeline._get_project(project_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not project.script:
        raise HTTPException(status_code=400, detail="Script must be generated first")

    # Run asset generation in background
    background_tasks.add_task(_run_asset_generation, project_id)
    return {"status": "started", "message": "Asset generation started"}


async def _run_asset_generation(project_id: str):
    from app.core.database import async_session
    async with async_session() as db:
        try:
            await pipeline.generate_assets(project_id, db)
        except Exception:
            pass  # Status tracked in pipeline


@router.get("/{project_id}/generate/assets/status", response_model=AssetStatusResponse)
async def get_asset_status(project_id: str):
    status = pipeline.get_asset_status(project_id)
    return AssetStatusResponse(**status)


@router.post("/{project_id}/generate/video")
async def generate_video(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    try:
        project = await pipeline._get_project(project_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if project.status not in ("assets_ready", "video_ready"):
        raise HTTPException(status_code=400, detail="Assets must be generated first")

    background_tasks.add_task(_run_video_generation, project_id)
    return {"status": "started", "message": "Video generation started"}


async def _run_video_generation(project_id: str):
    from app.core.database import async_session
    async with async_session() as db:
        try:
            await pipeline.generate_video(project_id, db)
        except Exception:
            pass  # Status tracked in pipeline


@router.get("/{project_id}/generate/video/status", response_model=VideoStatusResponse)
async def get_video_status(project_id: str):
    status = pipeline.get_video_status(project_id)
    return VideoStatusResponse(**status)
