from pydantic import BaseModel


class OutlineSection(BaseModel):
    title: str
    key_points: list[str]


class OutlineResponse(BaseModel):
    sections: list[OutlineSection]


class OutlineUpdate(BaseModel):
    sections: list[OutlineSection]


class ScriptScene(BaseModel):
    title: str
    narration: str
    visual_desc: str


class ScriptResponse(BaseModel):
    scenes: list[ScriptScene]


class ScriptUpdate(BaseModel):
    scenes: list[ScriptScene]


class AssetStatusResponse(BaseModel):
    status: str  # pending, in_progress, completed, failed
    progress: float  # 0.0 - 1.0
    message: str


class VideoStatusResponse(BaseModel):
    status: str  # pending, in_progress, completed, failed
    progress: float
    video_path: str | None = None
    message: str
