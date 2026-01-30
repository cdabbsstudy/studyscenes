import logging
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.services.base.image import ImageServiceBase

logger = logging.getLogger(__name__)

# Color palette for mock images
COLORS = [
    (41, 98, 255),    # Blue
    (0, 150, 136),    # Teal
    (156, 39, 176),   # Purple
    (255, 87, 34),    # Orange
    (76, 175, 80),    # Green
    (233, 30, 99),    # Pink
]

WIDTH, HEIGHT = 1280, 720
MARGIN_X = 80
MAX_TEXT_W = WIDTH - 2 * MARGIN_X
MAX_BULLET_CHARS = 70
MIN_BULLETS = 4
MAX_BULLETS = 6

FILLER_PREFIXES = re.compile(
    r"^(in this section,?\s*|next,?\s*we will\s*|now,?\s*let'?s?\s*|"
    r"here,?\s*we\s*|let'?s?\s*|we will\s*|we'll\s*|first,?\s*)",
    re.IGNORECASE,
)


def _bullets_from_key_points(key_points: list[str] | None) -> list[str] | None:
    """Return cleaned key_points if they provide enough bullets."""
    if not key_points:
        return None
    cleaned = [p.strip() for p in key_points if p.strip()]
    if len(cleaned) < 2:
        return None
    return cleaned


def _bullets_from_narration(narration: str) -> list[str]:
    """Derive bullet phrases from narration sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", narration.strip())
    bullets: list[str] = []
    for s in sentences:
        s = s.strip().rstrip(".!?").strip()
        if not s:
            continue
        # Strip filler openings
        s = FILLER_PREFIXES.sub("", s).strip()
        # Capitalize first letter
        if s:
            s = s[0].upper() + s[1:]
        if s:
            bullets.append(s)
    return bullets


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "\u2026"


def _build_bullets(
    key_points: list[str] | None,
    narration: str,
    visual_desc: str,
) -> tuple[list[str], str]:
    """Build 4-6 bullets. Returns (bullets, source_label)."""

    # Priority a: structured key_points from outline
    from_kp = _bullets_from_key_points(key_points)
    if from_kp and len(from_kp) >= MIN_BULLETS:
        bullets = [_truncate(b, MAX_BULLET_CHARS) for b in from_kp[:MAX_BULLETS]]
        return bullets, "outline"

    # Priority b: derive from narration
    from_narr = _bullets_from_narration(narration) if narration else []

    # Merge: prefer key_points first, pad with narration-derived
    merged: list[str] = []
    if from_kp:
        merged.extend(from_kp)
    for b in from_narr:
        if b not in merged:
            merged.append(b)

    if len(merged) >= MIN_BULLETS:
        bullets = [_truncate(b, MAX_BULLET_CHARS) for b in merged[:MAX_BULLETS]]
        source = "outline+narration" if from_kp else "narration"
        return bullets, source

    # Fallback: also try visual_desc sentences
    from_vd = re.split(r"[.!?]+", visual_desc)
    for s in from_vd:
        s = s.strip()
        if s and s not in merged:
            merged.append(s)

    bullets = [_truncate(b, MAX_BULLET_CHARS) for b in merged[:MAX_BULLETS]]
    source = "narration" if not from_kp else "outline+narration"
    return bullets, source


class MockImageService(ImageServiceBase):
    _color_index = 0

    async def generate(
        self,
        scene_title: str,
        visual_desc: str,
        output_path: Path,
        *,
        narration: str = "",
        key_points: list[str] | None = None,
    ) -> None:
        bg_color = COLORS[MockImageService._color_index % len(COLORS)]
        MockImageService._color_index += 1

        img = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
        draw = ImageDraw.Draw(img)

        title_size = 44
        bullet_size = 28
        small_size = 20
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", title_size)
            bullet_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", bullet_size)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", small_size)
        except (OSError, IOError):
            title_font = ImageFont.load_default()
            bullet_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # --- Title (centered, wrapped) ---
        wrapped_title = textwrap.fill(scene_title, width=40)
        title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]
        title_y = 50
        draw.text(
            ((WIDTH - title_w) / 2, title_y),
            wrapped_title,
            fill="white",
            font=title_font,
        )

        # --- Divider line ---
        div_y = title_y + title_h + 24
        draw.line(
            [(MARGIN_X, div_y), (WIDTH - MARGIN_X, div_y)],
            fill=(255, 255, 255, 180),
            width=2,
        )

        # --- Bullets ---
        bullets, source = _build_bullets(key_points, narration, visual_desc)
        bullet_y = div_y + 20
        line_spacing = 42
        bottom_safe = HEIGHT - 50

        rendered_count = 0
        for bullet_text in bullets:
            wrapped = textwrap.fill(f"\u2022  {bullet_text}", width=55)
            line_count = wrapped.count("\n") + 1
            needed = line_count * line_spacing

            if bullet_y + needed > bottom_safe:
                # Try smaller font as last resort
                if bullet_size > 22:
                    bullet_size = 22
                    line_spacing = 34
                    try:
                        bullet_font = ImageFont.truetype(
                            "/System/Library/Fonts/Helvetica.ttc", bullet_size
                        )
                    except (OSError, IOError):
                        pass
                    # Recheck with smaller font
                    wrapped = textwrap.fill(f"\u2022  {bullet_text}", width=65)
                    line_count = wrapped.count("\n") + 1
                    needed = line_count * line_spacing
                    if bullet_y + needed > bottom_safe:
                        break
                else:
                    break

            draw.text(
                (MARGIN_X + 10, bullet_y),
                wrapped,
                fill="white",
                font=bullet_font,
            )
            bullet_y += needed
            rendered_count += 1

        # --- MOCK watermark ---
        draw.text(
            (WIDTH - 120, HEIGHT - 40),
            "MOCK",
            fill=(255, 255, 255, 100),
            font=small_font,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG")

        logger.info(
            "MockImage: '%s' — %d bullets (source=%s)",
            scene_title, rendered_count, source,
        )
