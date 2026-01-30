from app.core.config import settings
from app.services.base.outline import OutlineServiceBase
from app.services.base.script import ScriptServiceBase
from app.services.base.voice import VoiceServiceBase
from app.services.base.image import ImageServiceBase
from app.services.base.video import VideoServiceBase


def get_outline_service() -> OutlineServiceBase:
    if settings.USE_MOCK_AI:
        from app.services.mock.outline import MockOutlineService
        return MockOutlineService()
    from app.services.real.outline import RealOutlineService
    return RealOutlineService()


def get_script_service() -> ScriptServiceBase:
    if settings.USE_MOCK_AI:
        from app.services.mock.script import MockScriptService
        return MockScriptService()
    raise NotImplementedError("Real script service not yet implemented")


def get_voice_service() -> VoiceServiceBase:
    if settings.USE_MOCK_AI:
        from app.services.mock.voice import MockVoiceService
        return MockVoiceService()
    raise NotImplementedError("Real voice service not yet implemented")


def get_image_service() -> ImageServiceBase:
    if settings.USE_MOCK_AI:
        from app.services.mock.image import MockImageService
        return MockImageService()
    raise NotImplementedError("Real image service not yet implemented")


def get_video_service() -> VideoServiceBase:
    from app.services.video import FFmpegVideoService
    return FFmpegVideoService()
