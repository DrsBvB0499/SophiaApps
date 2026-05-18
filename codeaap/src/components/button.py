import pygame
import math
from src.config import (TEXT_LIGHT, BUTTON_RADIUS, get_font,
                        PRIMARY, SECONDARY, ACCENT, PANEL_BG)


class Button:
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, color=None, text_color=None,
                 font_size: int = 32, icon: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.base_rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or PRIMARY
        self.text_color = text_color or (45, 52, 54)
        self.font = get_font(font_size, header=True)
        self.icon = icon

        self._hovered = False
        self._scale = 1.0
        self._target_scale = 1.0
        self._hover_t = 0.0          # 0..1 progress

        self.enabled = True
        self._click_flash = 0        # frames

    def update(self, dt: float) -> None:
        target = 1.05 if self._hovered and self.enabled else 1.0
        speed = 8.0
        self._scale += (target - self._scale) * min(1.0, speed * dt)

        if self._click_flash > 0:
            self._click_flash -= 1

        cx = self.base_rect.centerx
        cy = self.base_rect.centery
        w = int(self.base_rect.width * self._scale)
        h = int(self.base_rect.height * self._scale)
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True on click."""
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._click_flash = 6
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        color = self.color if self.enabled else (100, 100, 120)
        if self._click_flash > 0:
            color = tuple(min(255, c + 40) for c in color)

        shadow_rect = self.rect.move(0, 4)
        shadow_color = tuple(max(0, c - 60) for c in color)
        pygame.draw.rect(surface, shadow_color, shadow_rect,
                         border_radius=BUTTON_RADIUS)
        pygame.draw.rect(surface, color, self.rect,
                         border_radius=BUTTON_RADIUS)

        label = (self.icon + " " if self.icon else "") + self.text
        text_surf = self.font.render(label, True, self.text_color
                                     if self.enabled else (160, 160, 180))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
