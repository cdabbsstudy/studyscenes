from pathlib import Path

from pydub import AudioSegment
from pydub.generators import Sine

from app.services.base.voice import VoiceServiceBase
from app.schemas.generation import ScriptResponse


class MockVoiceService(VoiceServiceBase):
    async def generate(self, script: ScriptResponse, output_path: Path) -> float:
        # Calculate total duration from word count at 150 WPM
        total_words = sum(len(scene.narration.split()) for scene in script.scenes)
        total_duration_sec = max((total_words / 150) * 60, 5.0)
        total_duration_ms = int(total_duration_sec * 1000)

        # Generate a silent audio file with a subtle tone so it's not completely empty
        silence = AudioSegment.silent(duration=total_duration_ms)
        # Add a very quiet background tone so video players show audio is present
        tone = Sine(440).to_audio_segment(duration=total_duration_ms).apply_gain(-40)
        audio = silence.overlay(tone)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        audio.export(str(output_path), format="mp3")

        return total_duration_sec
