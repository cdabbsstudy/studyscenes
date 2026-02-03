import asyncio
import math
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

    def _vf_filter(self, title: str, base: str = "scale=1280:720") -> str:
        """Build the -vf filter string. Includes drawtext only if available."""
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
            segment_paths: list[Path] = []
            for i, scene in enumerate(scenes):
                seg_path = tmp_dir / f"segment_{i:03d}.mp4"
                await self._make_segment(scene, seg_path, tmp_dir)
                segment_paths.append(seg_path)

            if len(segment_paths) == 1:
                shutil.copy2(segment_paths[0], output_path)
            else:
                await self._concat(segment_paths, output_path, tmp_dir)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    async def _make_segment(
        self, scene: SceneInput, seg_path: Path, tmp_dir: Path
    ) -> None:
        """Dispatch based on visual_path suffix."""
        if scene.visual_path.suffix == ".mp4":
            await self._mux_clip_and_audio(scene, seg_path, tmp_dir)
        else:
            await self._mux_image_and_audio(scene, seg_path)

    async def _mux_clip_and_audio(
        self, scene: SceneInput, seg_path: Path, tmp_dir: Path
    ) -> None:
        """Align video clip duration to audio, then mux together."""
        clip_dur = await self._probe_duration(scene.visual_path)
        audio_dur = scene.duration_sec

        # Align clip duration to audio duration
        aligned_path = tmp_dir / f"aligned_{seg_path.stem}.mp4"

        if audio_dur > clip_dur and clip_dur > 0:
            # Loop the clip to cover the audio duration
            loops_needed = math.ceil(audio_dur / clip_dur) - 1
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", str(loops_needed),
                "-i", str(scene.visual_path),
                "-t", str(audio_dur),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                str(aligned_path),
            ]
            await self._run(cmd)
        elif audio_dur < clip_dur:
            # Trim the clip to audio duration
            cmd = [
                "ffmpeg", "-y",
                "-i", str(scene.visual_path),
                "-t", str(audio_dur),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                str(aligned_path),
            ]
            await self._run(cmd)
        else:
            aligned_path = scene.visual_path

        # Mux aligned video + audio
        cmd = [
            "ffmpeg", "-y",
            "-i", str(aligned_path),
            "-i", str(scene.audio_path),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "128k",
            "-map", "0:v",
            "-map", "1:a",
            "-shortest",
            str(seg_path),
        ]
        await self._run(cmd)

    async def _mux_image_and_audio(
        self, scene: SceneInput, seg_path: Path
    ) -> None:
        """Still-image + audio mux (original behavior)."""
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(scene.visual_path),
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
            str(seg_path),
        ]
        await self._run(cmd)

    async def _probe_duration(self, path: Path) -> float:
        """Get media file duration in seconds via ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 0.0

    async def _concat(
        self, segment_paths: list[Path], output_path: Path, tmp_dir: Path
    ) -> None:
        concat_file = tmp_dir / "concat.txt"
        lines = [f"file '{p}'\n" for p in segment_paths]
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
