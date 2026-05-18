import pygame
from src.config import SECONDARY, PANEL_BG, TEXT_LIGHT, get_font, PRIMARY


def draw_xp_bar(surface: pygame.Surface, x: int, y: int,
                width: int, height: int,
                player_xp: int, player_level: int,
                xp_per_level: int = 200) -> None:
    xp_in_level = player_xp % xp_per_level
    ratio = xp_in_level / xp_per_level

    # Background
    pygame.draw.rect(surface, PANEL_BG, (x, y, width, height), border_radius=8)

    # Fill
    fill_w = int(width * ratio)
    if fill_w > 0:
        pygame.draw.rect(surface, SECONDARY,
                         (x, y, fill_w, height), border_radius=8)

    # Border
    pygame.draw.rect(surface, PRIMARY, (x, y, width, height),
                     width=2, border_radius=8)

    # Label
    font = get_font(18)
    lbl = font.render(f"Level {player_level}  •  {xp_in_level}/{xp_per_level} XP",
                      True, TEXT_LIGHT)
    surface.blit(lbl, (x + width + 10, y + height // 2 - lbl.get_height() // 2))
