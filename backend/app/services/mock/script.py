from app.services.base.script import ScriptServiceBase
from app.schemas.generation import OutlineResponse, ScriptResponse, ScriptScene


class MockScriptService(ScriptServiceBase):
    async def generate(self, outline: OutlineResponse) -> ScriptResponse:
        scenes = []
        for i, section in enumerate(outline.sections):
            key_points_text = ". ".join(section.key_points)
            narration = (
                f"In this section, we'll cover {section.title}. "
                f"{key_points_text}. "
                f"These are important concepts to understand as we continue our study."
            )
            visual_desc = (
                f"Educational slide showing '{section.title}' as the heading "
                f"with key points listed below: {', '.join(section.key_points[:2])}."
            )
            scenes.append(ScriptScene(
                title=section.title,
                narration=narration,
                visual_desc=visual_desc,
            ))

        return ScriptResponse(scenes=scenes)
