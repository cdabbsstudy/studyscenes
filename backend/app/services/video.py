import asyncio
import tempfile
import shutil
from pathlib import Path

from app.services.base.video import VideoServiceBase, SceneInput


async def _check_drawtext() -> bool:
    """Check if FFmpeg was built with the drawtext filter."""
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-filters",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return b"drawtext" in stdout


class FFmpegVideoService(VideoServiceBase):
    _has_drawtext: bool | None = None

    async def _drawtext_available(self) -> bool:
        if FFmpegVideoService._has_drawtext is None:
            FFmpegVideoService._has_drawtext = await _check_drawtext()
        return FFmpegVideoService._has_drawtext

    def _vf_filter(self, title: str) -> str:
        """Build the -vf filter string. Includes drawtext only if available."""
        base = "scale=1280:720"
        if FFmpegVideoService._has_drawtext:
            return (
                f"{base},drawtext=text='{self._escape(title)}'"
                f":fontsize=36:fontcolor=white:borderw=2:bordercolor=black"
                f":x=(w-text_w)/2:y=40"
            )
        return base

    async def stitch(
        self,
        scenes: list[SceneInput],
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_dir = Path(tempfile.mkdtemp(prefix="studyscenes_"))

        await self._drawtext_available()

        try:
            if len(scenes) == 1:
                await self._single_scene(scenes[0], output_path)
            else:
                await self._multi_scene(scenes, output_path, tmp_dir)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    async def _single_scene(self, scene: SceneInput, output_path: Path) -> None:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(scene.image_path),
            "-i", str(scene.audio_path),
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-vf", self._vf_filter(scene.title),
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-movflags", "+faststart",
            str(output_path),
        ]
        await self._run(cmd)

    async def _multi_scene(
        self, scenes: list[SceneInput], output_path: Path, tmp_dir: Path
    ) -> None:
        clip_paths: list[Path] = []
        for i, scene in enumerate(scenes):
            clip_path = tmp_dir / f"clip_{i:03d}.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(scene.image_path),
                "-i", str(scene.audio_path),
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-vf", self._vf_filter(scene.title),
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-map", "0:v:0",
                "-map", "1:a:0",
                str(clip_path),
            ]
            await self._run(cmd)
            clip_paths.append(clip_path)

        # Concatenate all clips via concat demuxer
        concat_file = tmp_dir / "concat.txt"
        lines = [f"file '{p}'\n" for p in clip_paths]
        concat_file.write_text("".join(lines))

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            "-movflags", "+faststart",
            str(output_path),
        ]
        await self._run(cmd)

    @staticmethod
    def _escape(text: str) -> str:
        text = text.replace("\\", "\\\\")
        text = text.replace(":", "\\:")
        text = text.replace("'", "\\'")
        return text

    @staticmethod
    async def _run(cmd: list[str]) -> None:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()[-500:]}")
