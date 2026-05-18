import pygame
from src.config import (TEXT_LIGHT, BUTTON_RADIUS, get_font,
                        BLOCK_COLORS, TEXT_DARK)


class CodeBlock:
    """A clickable code-block card used in level scenes."""

    HEIGHT = 64
    MIN_WIDTH = 180

    def __init__(self, x: int, y: int, label: str, color_index: int = 0,
                 font_size: int = 26):
        self.label = label
        self.color = BLOCK_COLORS[color_index % len(BLOCK_COLORS)]
        self.font = get_font(font_size, header=True)

        text_surf = self.font.render(label, True, TEXT_DARK)
        width = max(self.MIN_WIDTH, text_surf.get_width() + 40)

        self.base_rect = pygame.Rect(x, y, width, self.HEIGHT)
        self.rect = self.base_rect.copy()
        self._hovered = False
        self._scale = 1.0
        self.enabled = True
        self.visible = True
        self._click_flash = 0

    def move_to(self, x: int, y: int) -> None:
        self.base_rect.topleft = (x, y)
        self.rect.topleft = (x, y)

    def update(self, dt: float) -> None:
        if not self.visible:
            return
        target = 1.06 if self._hovered and self.enabled else 1.0
        self._scale += (target - self._scale) * min(1.0, 8.0 * dt)

        if self._click_flash > 0:
            self._click_flash -= 1

        cx = self.base_rect.centerx
        cy = self.base_rect.centery
        w = int(self.base_rect.width * self._scale)
        h = int(self.base_rect.height * self._scale)
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._click_flash = 5
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        color = self.color if self.enabled else (120, 120, 140)
        if self._click_flash > 0:
            color = tuple(min(255, c + 50) for c in color)

        shadow = self.rect.move(0, 3)
        shadow_c = tuple(max(0, c - 60) for c in color)
        pygame.draw.rect(surface, shadow_c, shadow, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(surface, color, self.rect, border_radius=BUTTON_RADIUS)

        text_surf = self.font.render(self.label, True,
                                     TEXT_DARK if self.enabled else (160, 160, 160))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
