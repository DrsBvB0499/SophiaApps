import pygame
import math
from src.config import STAR_COLOR, STAR_EMPTY


def draw_stars(surface: pygame.Surface, cx: int, cy: int,
               stars: int, max_stars: int = 3,
               size: int = 40, gap: int = 10) -> None:
    """Draw star-rating centred at (cx, cy)."""
    total_w = max_stars * size * 2 + (max_stars - 1) * gap
    start_x = cx - total_w // 2
    for i in range(max_stars):
        sx = start_x + i * (size * 2 + gap) + size
        color = STAR_COLOR if i < stars else STAR_EMPTY
        _draw_star(surface, sx, cy, size, color)


def _draw_star(surface: pygame.Surface, cx: int, cy: int,
               r: int, color: tuple) -> None:
    pts = []
    for i in range(10):
        angle = math.radians(-90 + 36 * i)
        radius = r if i % 2 == 0 else r * 0.45
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        pts.append((x, y))
    pygame.draw.polygon(surface, color, pts)
    # Thin outline
    pygame.draw.polygon(surface, (200, 150, 0) if color != STAR_EMPTY else (60, 60, 80),
                        pts, 2)
