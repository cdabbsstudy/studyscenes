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
        audio_path: Path,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_dir = Path(tempfile.mkdtemp(prefix="studyscenes_"))

        # Probe drawtext support once before we start
        await self._drawtext_available()

        try:
            if len(scenes) == 1:
                await self._single_scene(scenes[0], audio_path, output_path, tmp_dir)
            else:
                await self._multi_scene(scenes, audio_path, output_path, tmp_dir)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    async def _single_scene(
        self, scene: SceneInput, audio_path: Path, output_path: Path, tmp_dir: Path
    ) -> None:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(scene.image_path),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-t", str(scene.duration_sec),
            "-pix_fmt", "yuv420p",
            "-vf", self._vf_filter(scene.title),
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path),
        ]
        await self._run(cmd)

    async def _multi_scene(
        self, scenes: list[SceneInput], audio_path: Path, output_path: Path, tmp_dir: Path
    ) -> None:
        # Create per-scene video clips
        clip_paths = []
        for i, scene in enumerate(scenes):
            clip_path = tmp_dir / f"clip_{i:03d}.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(scene.image_path),
                "-c:v", "libx264",
                "-t", str(scene.duration_sec),
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-vf", self._vf_filter(scene.title),
                "-an",
                str(clip_path),
            ]
            await self._run(cmd)
            clip_paths.append(clip_path)

        # Try xfade crossfades; fall back to simple concat on failure
        merged_video = tmp_dir / "merged.mp4"
        try:
            await self._xfade_merge(clip_paths, scenes, merged_video)
        except RuntimeError:
            await self._concat_merge(clip_paths, merged_video, tmp_dir)

        # Mux merged video with audio
        cmd = [
            "ffmpeg", "-y",
            "-i", str(merged_video),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path),
        ]
        await self._run(cmd)

    async def _xfade_merge(
        self, clip_paths: list[Path], scenes: list[SceneInput], output: Path
    ) -> None:
        xfade_dur = 0.5
        n = len(clip_paths)
        if n < 2:
            shutil.copy(clip_paths[0], output)
            return

        # Build complex xfade filter chain
        inputs = []
        for p in clip_paths:
            inputs.extend(["-i", str(p)])

        filter_parts = []
        offsets = []
        cumulative = 0.0
        for i, scene in enumerate(scenes):
            if i < n - 1:
                offset = cumulative + scene.duration_sec - xfade_dur
                offsets.append(offset)
            cumulative += scene.duration_sec - (xfade_dur if i < n - 1 else 0)

        # Chain xfade filters
        prev = "[0:v]"
        for i in range(n - 1):
            next_input = f"[{i + 1}:v]"
            out_label = f"[v{i}]" if i < n - 2 else "[vout]"
            filter_parts.append(
                f"{prev}{next_input}xfade=transition=fade:duration={xfade_dur}"
                f":offset={offsets[i]:.3f}{out_label}"
            )
            prev = out_label

        filter_str = ";".join(filter_parts)
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_str,
            "-map", "[vout]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output),
        ]
        await self._run(cmd)

    async def _concat_merge(
        self, clip_paths: list[Path], output: Path, tmp_dir: Path
    ) -> None:
        concat_file = tmp_dir / "concat.txt"
        lines = [f"file '{p}'\n" for p in clip_paths]
        concat_file.write_text("".join(lines))

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output),
        ]
        await self._run(cmd)

    @staticmethod
    def _escape(text: str) -> str:
        # Escape special characters for FFmpeg drawtext filter
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
