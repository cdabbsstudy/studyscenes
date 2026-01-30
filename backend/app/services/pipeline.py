from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.scene import Scene
from app.schemas.generation import OutlineResponse, ScriptResponse
from app.services.factory import (
    get_outline_service,
    get_script_service,
    get_voice_service,
    get_image_service,
    get_video_service,
)
from app.services.storage import LocalFileStorage
from app.services.base.video import SceneInput

# In-memory status tracking (sufficient for MVP single-process)
_asset_status: dict[str, dict] = {}
_video_status: dict[str, dict] = {}

storage = LocalFileStorage()


def get_asset_status(project_id: str) -> dict:
    return _asset_status.get(project_id, {
        "status": "pending", "progress": 0.0, "message": "Not started"
    })


def get_video_status(project_id: str) -> dict:
    return _video_status.get(project_id, {
        "status": "pending", "progress": 0.0, "video_path": None, "message": "Not started"
    })


async def generate_outline(project_id: str, db: AsyncSession) -> OutlineResponse:
    project = await _get_project(project_id, db)
    svc = get_outline_service()
    outline = await svc.generate(project.content)

    project.outline = outline.model_dump()
    project.status = "outline_ready"
    await db.commit()
    return outline


async def save_outline(project_id: str, outline: OutlineResponse, db: AsyncSession) -> None:
    project = await _get_project(project_id, db)
    project.outline = outline.model_dump()
    project.status = "outline_ready"
    await db.commit()


async def generate_script(project_id: str, db: AsyncSession) -> ScriptResponse:
    project = await _get_project(project_id, db)
    if not project.outline:
        raise ValueError("Outline must be generated first")

    svc = get_script_service()
    outline = OutlineResponse(**project.outline)
    script = await svc.generate(outline)

    project.script = script.model_dump()
    project.status = "script_ready"

    # Create/update scene records
    await _sync_scenes(project, script, db)
    await db.commit()
    return script


async def save_script(project_id: str, script: ScriptResponse, db: AsyncSession) -> None:
    project = await _get_project(project_id, db)
    project.script = script.model_dump()
    project.status = "script_ready"
    await _sync_scenes(project, script, db)
    await db.commit()


async def generate_assets(project_id: str, db: AsyncSession) -> None:
    project = await _get_project(project_id, db, load_scenes=True)
    if not project.script:
        raise ValueError("Script must be generated first")

    script = ScriptResponse(**project.script)
    outline = OutlineResponse(**project.outline) if project.outline else None
    total_steps = len(script.scenes) * 2  # image + audio per scene
    done = 0

    _asset_status[project_id] = {
        "status": "in_progress", "progress": 0.0, "message": "Starting asset generation..."
    }

    try:
        image_svc = get_image_service()
        voice_svc = get_voice_service()

        for i, scene_data in enumerate(script.scenes):
            # Resolve outline key_points for this scene (matched by index)
            key_points = None
            if outline and i < len(outline.sections):
                key_points = outline.sections[i].key_points

            # Generate image
            img_path = storage.scene_image_path(project_id, i)
            await image_svc.generate(
                scene_data.title,
                scene_data.visual_desc,
                img_path,
                narration=scene_data.narration,
                key_points=key_points,
            )

            if i < len(project.scenes):
                project.scenes[i].image_path = f"/storage/{storage.relative_path(img_path)}"

            done += 1
            _asset_status[project_id] = {
                "status": "in_progress",
                "progress": done / total_steps,
                "message": f"Generated image {i + 1}/{len(script.scenes)}",
            }

            # Generate per-scene audio
            audio_path = storage.scene_audio_path(project_id, i)
            duration = await voice_svc.generate_scene(scene_data.narration, audio_path)

            if i < len(project.scenes):
                project.scenes[i].duration_sec = duration

            done += 1
            _asset_status[project_id] = {
                "status": "in_progress",
                "progress": done / total_steps,
                "message": f"Generated audio {i + 1}/{len(script.scenes)}",
            }

        project.status = "assets_ready"
        await db.commit()

        _asset_status[project_id] = {
            "status": "completed", "progress": 1.0, "message": "All assets generated"
        }
    except Exception as e:
        _asset_status[project_id] = {
            "status": "failed", "progress": done / total_steps, "message": str(e)
        }
        raise


async def generate_video(project_id: str, db: AsyncSession) -> str:
    project = await _get_project(project_id, db, load_scenes=True)
    if project.status not in ("assets_ready", "video_ready"):
        raise ValueError("Assets must be generated first")

    _video_status[project_id] = {
        "status": "in_progress", "progress": 0.3, "video_path": None, "message": "Stitching video..."
    }

    try:
        scene_inputs = []
        for i, scene in enumerate(project.scenes):
            if not scene.image_path:
                raise ValueError(f"Scene {scene.order_index} missing image")
            img_fs_path = storage.base / scene.image_path.replace("/storage/", "")
            audio_fs_path = storage.scene_audio_path(project_id, i)
            scene_inputs.append(SceneInput(
                image_path=img_fs_path,
                audio_path=audio_fs_path,
                title=scene.title,
                duration_sec=scene.duration_sec,
            ))

        output_path = storage.video_output_path(project_id)

        video_svc = get_video_service()
        await video_svc.stitch(scene_inputs, output_path)

        video_url = f"/storage/{storage.relative_path(output_path)}"
        project.video_path = video_url
        project.status = "video_ready"
        await db.commit()

        _video_status[project_id] = {
            "status": "completed", "progress": 1.0,
            "video_path": video_url, "message": "Video ready"
        }
        return video_url
    except Exception as e:
        _video_status[project_id] = {
            "status": "failed", "progress": 0.0, "video_path": None, "message": str(e)
        }
        raise


async def _get_project(project_id: str, db: AsyncSession, load_scenes: bool = False) -> Project:
    stmt = select(Project).where(Project.id == project_id)
    if load_scenes:
        stmt = stmt.options(selectinload(Project.scenes))
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError(f"Project {project_id} not found")
    return project


async def _sync_scenes(project: Project, script: ScriptResponse, db: AsyncSession) -> None:
    # Delete existing scenes
    result = await db.execute(
        select(Scene).where(Scene.project_id == project.id)
    )
    for old_scene in result.scalars().all():
        await db.delete(old_scene)

    # Create new scenes
    for i, scene_data in enumerate(script.scenes):
        words = len(scene_data.narration.split())
        duration = max((words / 150) * 60, 2.0)
        scene = Scene(
            project_id=project.id,
            order_index=i,
            title=scene_data.title,
            narration=scene_data.narration,
            visual_desc=scene_data.visual_desc,
            duration_sec=duration,
        )
        db.add(scene)
