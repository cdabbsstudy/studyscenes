import json
import logging

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings
from app.schemas.generation import OutlineResponse, OutlineSection
from app.services.base.outline import OutlineServiceBase

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate structured outlines from study material.\n"
    "Return ONLY valid JSON, no markdown fences, no extra text.\n"
    'Format: {"sections": [{"title": "...", "key_points": ["...", "..."]}]}\n'
    "Rules: 4-8 sections, 3-6 key_points per section."
)


class RealOutlineService(OutlineServiceBase):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when USE_MOCK_AI is disabled"
            )
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(self, content: str) -> OutlineResponse:
        logger.info("Generating outline via OpenAI (model=gpt-4o-mini)")
        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                temperature=0.7,
            )
        except OpenAIError as exc:
            logger.error("OpenAI API error: %s", exc)
            raise RuntimeError(f"OpenAI error: {exc}") from exc

        raw = response.choices[0].message.content
        logger.debug("OpenAI raw response: %s", raw)

        try:
            data = json.loads(raw)
            sections = [
                OutlineSection(title=s["title"], key_points=s["key_points"])
                for s in data["sections"]
            ]
            return OutlineResponse(sections=sections)
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.error("Failed to parse outline JSON: %s", exc)
            raise RuntimeError(f"Failed to parse outline: {exc}") from exc
