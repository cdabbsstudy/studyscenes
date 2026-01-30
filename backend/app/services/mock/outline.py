import re

from app.services.base.outline import OutlineServiceBase
from app.schemas.generation import OutlineResponse, OutlineSection


class MockOutlineService(OutlineServiceBase):
    async def generate(self, content: str) -> OutlineResponse:
        # Split content into paragraphs and create sections
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]

        if not paragraphs:
            paragraphs = [content[:200]] if content else ["No content provided"]

        sections = []
        for i, para in enumerate(paragraphs[:6]):  # Cap at 6 sections
            words = para.split()
            title = " ".join(words[:5]).rstrip(".,;:") or f"Section {i + 1}"
            # Extract key points from sentences
            sentences = [s.strip() for s in re.split(r"[.!?]+", para) if s.strip()]
            key_points = sentences[:3] if sentences else [para[:100]]
            sections.append(OutlineSection(title=title, key_points=key_points))

        if not sections:
            sections = [
                OutlineSection(title="Introduction", key_points=["Overview of the topic"]),
                OutlineSection(title="Key Concepts", key_points=["Main ideas and themes"]),
                OutlineSection(title="Summary", key_points=["Review of main points"]),
            ]

        return OutlineResponse(sections=sections)
