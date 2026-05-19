import pygame
from src.config import (BG_COLOR, PRIMARY, SECONDARY, TEXT_LIGHT,
                         TEXT_DARK, SCREEN_WIDTH, SCREEN_HEIGHT,
                         PANEL_BG, get_font)
from src.components.button import Button
from src.components.badge import BadgeTile, BADGE_DEFS
from src import sounds


class AchievementsScene:
    def __init__(self, progress: dict):
        self.progress = progress
        self._next_scene: str | None = None

        self._back_btn = Button(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 80,
                                 240, 60, "← Terug", PRIMARY, TEXT_DARK, 28)

        self._font_title = get_font(44, header=True)
        self._font_small = get_font(18)

        self._tiles: list[BadgeTile] = []
        self._build_tiles()

        self._scroll_y = 0
        self._max_scroll = 0

    def _build_tiles(self) -> None:
        earned = set(self.progress.get("badges_earned", []))
        all_badge_ids = list(BADGE_DEFS.keys())
        cols = 6
        tile_size = BadgeTile.SIZE
        gap = 16
        total_w = cols * tile_size + (cols - 1) * gap
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        start_y = 120

        for idx, bid in enumerate(all_badge_ids):
            col = idx % cols
            row = idx // cols
            x = start_x + col * (tile_size + gap)
            y = start_y + row * (tile_size + gap + 20)
            self._tiles.append(BadgeTile(x, y, bid, bid in earned))

        rows = (len(all_badge_ids) + cols - 1) // cols
        total_h = start_y + rows * (tile_size + gap + 20) + 20
        self._max_scroll = max(0, total_h - (SCREEN_HEIGHT - 100))

    # ------------------------------------------------------------------
    def next_scene(self) -> str | None:
        s = self._next_scene
        self._next_scene = None
        return s

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._back_btn.handle_event(event):
            sounds.play("click")
            self._next_scene = "menu"
            return

        if event.type == pygame.MOUSEWHEEL:
            self._scroll_y = max(0, min(self._max_scroll,
                                         self._scroll_y - event.y * 30))

        for tile in self._tiles:
            tile.handle_event(event)

    def update(self, dt: float) -> None:
        self._back_btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)

        title = self._font_title.render("Mijn Badges", True, PRIMARY)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        earned = len(self.progress.get("badges_earned", []))
        total  = len(BADGE_DEFS)
        sub = self._font_small.render(
            f"{earned} van {total} badges behaald", True, (180, 180, 200))
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 96)))

        # Clip tile area
        clip_rect = pygame.Rect(0, 110, SCREEN_WIDTH, SCREEN_HEIGHT - 200)
        surface.set_clip(clip_rect)

        for tile in self._tiles:
            tile.y = tile.rect.y - self._scroll_y
            # quick draw offset without moving rect permanently
            orig_rect = tile.rect.copy()
            tile.rect.y = tile.y
            tile.draw(surface)
            tile.rect = orig_rect

        surface.set_clip(None)

        # Tooltip on hover
        for tile in self._tiles:
            if tile._hover and tile.unlocked:
                defn = BADGE_DEFS.get(tile.badge_id, {})
                desc = defn.get("desc", "")
                if desc:
                    tip = self._font_small.render(desc, True, TEXT_LIGHT)
                    tip_rect = tip.get_rect(
                        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
                    bg = tip_rect.inflate(20, 10)
                    pygame.draw.rect(surface, PANEL_BG, bg, border_radius=8)
                    surface.blit(tip, tip_rect)

        self._back_btn.draw(surface)
