import re

from app.services.base.outline import OutlineServiceBase
from app.schemas.generation import OutlineResponse, OutlineSection

MIN_SECTIONS = 8
MAX_SECTIONS = 12


class MockOutlineService(OutlineServiceBase):
    async def generate(self, content: str) -> OutlineResponse:
        # Split content into paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]

        if not paragraphs:
            paragraphs = [content[:200]] if content else ["No content provided"]

        # Split paragraphs into individual sentences for finer-grained sections
        all_sentences: list[str] = []
        for para in paragraphs:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
            all_sentences.extend(sentences)

        # Group 2-3 sentences per section to target 8-12 sections
        sections: list[OutlineSection] = []
        i = 0
        while i < len(all_sentences) and len(sections) < MAX_SECTIONS:
            # Take 2-3 sentences per group
            remaining = len(all_sentences) - i
            remaining_sections = MAX_SECTIONS - len(sections)
            group_size = max(1, min(3, remaining // max(1, remaining_sections)))
            group = all_sentences[i : i + group_size]
            i += group_size

            # Title from first sentence words
            words = group[0].split()
            title = " ".join(words[:5]).rstrip(".,;:") or f"Section {len(sections) + 1}"
            key_points = [s.rstrip(".!?").strip() for s in group if s.strip()]
            if not key_points:
                key_points = [group[0][:100]]

            sections.append(OutlineSection(title=title, key_points=key_points))

        # Pad with generic sections if fewer than MIN_SECTIONS
        generic = [
            ("Introduction", ["Overview of the topic", "Context and background"]),
            ("Key Concepts", ["Main ideas and themes", "Core definitions"]),
            ("Detailed Analysis", ["In-depth examination", "Supporting evidence"]),
            ("Mechanisms and Processes", ["Step-by-step breakdown", "How it works"]),
            ("Important Factors", ["Contributing elements", "Key variables"]),
            ("Applications", ["Real-world uses", "Practical implications"]),
            ("Connections and Relationships", ["How concepts relate", "Cause and effect"]),
            ("Summary and Review", ["Review of main points", "Key takeaways"]),
        ]
        gi = 0
        while len(sections) < MIN_SECTIONS and gi < len(generic):
            title, points = generic[gi]
            # Avoid duplicate titles
            if not any(s.title == title for s in sections):
                sections.append(OutlineSection(title=title, key_points=points))
            gi += 1

        return OutlineResponse(sections=sections)
