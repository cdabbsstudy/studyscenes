import logging
from pathlib import Path

from pydub import AudioSegment
from pydub.generators import Sine

from app.services.base.voice import VoiceServiceBase

logger = logging.getLogger(__name__)

BEEP_FREQ_HZ = 880
BEEP_ON_MS = 200
BEEP_OFF_MS = 200
BEEP_CYCLE_MS = BEEP_ON_MS + BEEP_OFF_MS
GAIN_DB = 9


class MockVoiceService(VoiceServiceBase):
    async def generate_scene(self, narration: str, output_path: Path) -> float:
        word_count = len(narration.split())
        duration_sec = max((word_count / 150) * 60, 2.0)
        duration_ms = int(duration_sec * 1000)

        beep = Sine(BEEP_FREQ_HZ).to_audio_segment(duration=BEEP_ON_MS).apply_gain(GAIN_DB)
        gap = AudioSegment.silent(duration=BEEP_OFF_MS)
        cycle = beep + gap

        repeats = (duration_ms // BEEP_CYCLE_MS) + 1
        audio = (cycle * repeats)[:duration_ms]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        audio.export(str(output_path), format="wav")

        logger.info("MockVoice: %.1fs audio written to %s", duration_sec, output_path)
        return duration_sec
