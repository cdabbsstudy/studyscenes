from app.core.config import settings
from app.services.base.outline import OutlineServiceBase
from app.services.base.script import ScriptServiceBase
from app.services.base.voice import VoiceServiceBase
from app.services.base.image import ImageServiceBase
from app.services.base.video import VideoServiceBase
from app.services.base.video_clip import VideoClipServiceBase


def get_outline_service() -> OutlineServiceBase:
    if settings.USE_MOCK_AI:
        from app.services.mock.outline import MockOutlineService
        return MockOutlineService()
    from app.services.real.outline import RealOutlineService
    return RealOutlineService()


def get_script_service() -> ScriptServiceBase:
    from app.services.mock.script import MockScriptService
    return MockScriptService()


def get_voice_service() -> VoiceServiceBase:
    if settings.USE_MOCK_TTS:
        from app.services.mock.voice import MockVoiceService
        return MockVoiceService()
    from app.services.real.voice import RealVoiceService
    return RealVoiceService()


def get_image_service() -> ImageServiceBase:
    from app.services.mock.image import MockImageService
    return MockImageService()


def get_video_clip_service() -> VideoClipServiceBase:
    if settings.VIDEO_PROVIDER == "runway":
        from app.services.real.video_clip import RunwayVideoClipService
        return RunwayVideoClipService()
    from app.services.mock.video_clip import MockVideoClipService
    return MockVideoClipService()


def get_video_service() -> VideoServiceBase:
    from app.services.video import FFmpegVideoService
    return FFmpegVideoService()
