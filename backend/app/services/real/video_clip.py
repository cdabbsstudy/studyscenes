import asyncio
import logging
from pathlib import Path

import httpx

from app.core.config import settings
from app.services.base.video_clip import VideoClipServiceBase

logger = logging.getLogger(__name__)

API_BASE = "https://api.dev.runwayml.com"
POLL_INTERVAL = 10  # seconds
POLL_TIMEOUT = 300  # seconds
VALID_DURATIONS = (4, 6, 8)


class RunwayVideoClipService(VideoClipServiceBase):
    """Generate video clips via Runway ML text-to-video API."""

    def __init__(self) -> None:
        if not settings.RUNWAY_API_KEY:
            raise ValueError(
                "RUNWAY_API_KEY is required when VIDEO_PROVIDER=runway"
            )
        self._headers = {
            "Authorization": f"Bearer {settings.RUNWAY_API_KEY}",
            "X-Runway-Version": "2024-11-06",
            "Content-Type": "application/json",
        }

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

        # Clamp duration to valid Runway values
        clamped = min(VALID_DURATIONS, key=lambda d: abs(d - duration_sec))

        # Build prompt
        prompt = f"{scene_title}: {visual_desc}"
        if narration:
            prompt += f" Context: {narration}"
        prompt = prompt[:1000]

        # Submit task
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{API_BASE}/v1/text_to_video",
                headers=self._headers,
                json={
                    "model": "gen3a_turbo",
                    "promptText": prompt,
                    "ratio": "1280:720",
                    "duration": clamped,
                },
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Runway API error {resp.status_code}: {resp.text[:500]}"
                )
            task_id = resp.json()["id"]
            logger.info("Runway task created: %s for '%s'", task_id, scene_title)

        # Poll for completion
        elapsed = 0
        async with httpx.AsyncClient(timeout=30) as client:
            while elapsed < POLL_TIMEOUT:
                await asyncio.sleep(POLL_INTERVAL)
                elapsed += POLL_INTERVAL

                resp = await client.get(
                    f"{API_BASE}/v1/tasks/{task_id}",
                    headers=self._headers,
                )
                if resp.status_code != 200:
                    raise RuntimeError(
                        f"Runway poll error {resp.status_code}: {resp.text[:500]}"
                    )

                data = resp.json()
                status = data.get("status")
                logger.debug("Runway task %s status: %s", task_id, status)

                if status == "SUCCEEDED":
                    output_url = data["output"][0]
                    await self._download(client, output_url, output_path)
                    logger.info("Runway clip saved: %s", output_path)
                    return
                elif status == "FAILED":
                    raise RuntimeError(
                        f"Runway task failed: {data.get('failure', 'unknown')}"
                    )

        raise RuntimeError(f"Runway task {task_id} timed out after {POLL_TIMEOUT}s")

    async def _download(
        self, client: httpx.AsyncClient, url: str, output_path: Path
    ) -> None:
        resp = await client.get(url)
        resp.raise_for_status()
        output_path.write_bytes(resp.content)
