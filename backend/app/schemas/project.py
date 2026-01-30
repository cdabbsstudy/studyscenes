from datetime import datetime
from pydantic import BaseModel


class SceneResponse(BaseModel):
    id: str
    project_id: str
    order_index: int
    title: str
    narration: str
    visual_desc: str
    image_path: str | None = None
    duration_sec: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    title: str
    content: str


class ProjectResponse(BaseModel):
    id: str
    title: str
    content: str
    outline: dict | None = None
    script: dict | None = None
    status: str
    video_path: str | None = None
    audio_path: str | None = None
    created_at: datetime
    updated_at: datetime
    scenes: list[SceneResponse] = []

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
