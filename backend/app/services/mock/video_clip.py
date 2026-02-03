import asyncio
import logging
import tempfile
from pathlib import Path

from app.services.base.video_clip import VideoClipServiceBase
from app.services.mock.image import MockImageService

logger = logging.getLogger(__name__)


class MockVideoClipService(VideoClipServiceBase):
    """Generate a Ken Burns zoom clip from a static mock slide image."""

    def __init__(self) -> None:
        self._image_svc = MockImageService()

    async def generate(
        self,
        scene_title: str,
        visual_desc: str,
        output_path: Path,
        *,
        narration: str = "",
        duration_sec: int = 6,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate the static slide image to a temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            slide_path = Path(tmp.name)

        try:
            await self._image_svc.generate(
                scene_title, visual_desc, slide_path, narration=narration
            )

            total_frames = duration_sec * 30
            vf = (
                f"zoompan="
                f"z='1+0.3*on/{total_frames}':"
                f"x='iw/2-(iw/zoom/2)+on*0.5':"
                f"y='ih/2-(ih/zoom/2)+on*0.3':"
                f"d={total_frames}:s=1280x720:fps=30"
            )

            cmd = [
                "ffmpeg", "-y",
                "-i", str(slide_path),
                "-vf", vf,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-t", str(duration_sec),
                str(output_path),
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg Ken Burns failed: {stderr.decode()[-500:]}")

            logger.info("MockVideoClip: '%s' → %s (%ds)", scene_title, output_path, duration_sec)
        finally:
            slide_path.unlink(missing_ok=True)
