from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.services.base.image import ImageServiceBase

# Color palette for mock images
COLORS = [
    (41, 98, 255),    # Blue
    (0, 150, 136),    # Teal
    (156, 39, 176),   # Purple
    (255, 87, 34),    # Orange
    (76, 175, 80),    # Green
    (233, 30, 99),    # Pink
]


class MockImageService(ImageServiceBase):
    _color_index = 0

    async def generate(self, scene_title: str, visual_desc: str, output_path: Path) -> None:
        width, height = 1280, 720
        bg_color = COLORS[MockImageService._color_index % len(COLORS)]
        MockImageService._color_index += 1

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Try to use a built-in font, fall back to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            desc_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except (OSError, IOError):
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()

        # Draw scene title centered
        title_bbox = draw.textbbox((0, 0), scene_title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(
            ((width - title_w) / 2, height / 3),
            scene_title,
            fill="white",
            font=title_font,
        )

        # Draw visual description below (truncated)
        desc_text = visual_desc[:80] + "..." if len(visual_desc) > 80 else visual_desc
        desc_bbox = draw.textbbox((0, 0), desc_text, font=desc_font)
        desc_w = desc_bbox[2] - desc_bbox[0]
        draw.text(
            ((width - desc_w) / 2, height / 2 + 30),
            desc_text,
            fill=(255, 255, 255, 200),
            font=desc_font,
        )

        # Draw "MOCK" watermark
        draw.text((width - 120, height - 40), "MOCK", fill=(255, 255, 255, 100), font=desc_font)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG")
