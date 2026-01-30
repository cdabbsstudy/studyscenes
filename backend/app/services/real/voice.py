import logging
import wave
from pathlib import Path

import openai

from app.core.config import settings
from app.services.base.voice import VoiceServiceBase

logger = logging.getLogger(__name__)


class RealVoiceService(VoiceServiceBase):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required for real TTS. "
                "Set it in .env or switch to USE_MOCK_TTS=true."
            )
        self._client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_scene(self, narration: str, output_path: Path) -> float:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            response = await self._client.audio.speech.create(
                model="tts-1",
                voice=settings.TTS_VOICE,
                input=narration,
                response_format="wav",
            )
        except openai.OpenAIError as exc:
            raise RuntimeError(f"OpenAI TTS error: {exc}") from exc

        audio_bytes = response.content
        output_path.write_bytes(audio_bytes)

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"TTS output file is empty or missing: {output_path}")

        duration = self._wav_duration(output_path)
        logger.info("RealVoice: %.1fs audio written to %s", duration, output_path)
        return duration

    @staticmethod
    def _wav_duration(path: Path) -> float:
        with wave.open(str(path), "rb") as wf:
            rate = wf.getframerate()
            frames = wf.getnframes()
            # OpenAI TTS sets nframes to INT32_MAX; fall back to file-size math
            if frames >= 2147483647:
                data_bytes = path.stat().st_size - 44  # 44-byte WAV header
                frame_size = wf.getnchannels() * wf.getsampwidth()
                frames = data_bytes // frame_size
            return frames / rate
