import pygame
import math
from src.config import (BG_COLOR, PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT,
                         TEXT_DARK, SCREEN_WIDTH, SCREEN_HEIGHT,
                         PANEL_BG, PANEL_BORDER, LOCKED_COLOR,
                         STAR_COLOR, get_font, XP_PER_LEVEL)
from src.components.button import Button
from src.components.progress_bar import draw_xp_bar
from src.components.star_display import draw_stars
from src import sounds


_ISLAND_COLORS = {
    1: (247, 183, 49),
    2: (32, 191, 107),
    3: (116, 185, 255),
}


class WorldMapScene:
    def __init__(self, progress: dict, levels_data: dict):
        self.progress = progress
        self.levels_data = levels_data
        self._next_scene: str | None = None
        self._next_level_info: tuple | None = None

        self._back_btn   = Button(20, 20, 140, 56, "← Menu", PANEL_BG, TEXT_LIGHT, 24)
        self._badge_btn  = Button(SCREEN_WIDTH - 170, 20, 140, 56, "Badges", PRIMARY, TEXT_DARK, 24)

        self._font_title   = get_font(28, header=True)
        self._font_island  = get_font(22, header=True)
        self._font_level   = get_font(20, header=True)
        self._font_small   = get_font(16)

        self._selected_island: int | None = None
        self._island_hover: int | None = None
        self._level_buttons: dict = {}     # island_id -> list of (rect, level_dict)
        self._island_rects: dict = {}      # island_id -> rect
        self._build_island_rects()

        self._anim_t = 0.0

    # ------------------------------------------------------------------
    def next_scene(self) -> str | None:
        s = self._next_scene
        self._next_scene = None
        return s

    def next_level_info(self) -> tuple | None:
        info = self._next_level_info
        self._next_level_info = None
        return info

    # ------------------------------------------------------------------
    def _build_island_rects(self) -> None:
        for island in self.levels_data["islands"]:
            iid = island["id"]
            pos = island.get("position", [200 + iid * 180, 400])
            r = 70
            self._island_rects[iid] = pygame.Rect(
                pos[0] - r, pos[1] - r, r * 2, r * 2)

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self._back_btn.handle_event(event):
            sounds.play("click")
            self._next_scene = "menu"
            return
        if self._badge_btn.handle_event(event):
            sounds.play("click")
            self._next_scene = "achievements"
            return

        if event.type == pygame.MOUSEMOTION:
            self._island_hover = None
            for iid, rect in self._island_rects.items():
                if rect.collidepoint(event.pos):
                    self._island_hover = iid

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check island click
            for iid, rect in self._island_rects.items():
                if rect.collidepoint(event.pos):
                    if iid in self.progress.get("islands_unlocked", [1]):
                        sounds.play("click")
                        if self._selected_island == iid:
                            self._selected_island = None
                        else:
                            self._selected_island = iid
                    return

            # Check level button click
            if self._selected_island:
                for btn_rect, lv in self._level_buttons.get(self._selected_island, []):
                    if btn_rect.collidepoint(event.pos):
                        if self._is_level_unlocked(self._selected_island, lv["id"]):
                            sounds.play("click")
                            self._next_level_info = (self._selected_island, lv)
                            self._next_scene = "level"
                        return

            # Click outside — deselect
            self._selected_island = None

    def update(self, dt: float) -> None:
        self._anim_t += dt
        self._back_btn.update(dt)
        self._badge_btn.update(dt)

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        self._draw_bg(surface)

        # Paths between islands
        self._draw_paths(surface)

        # Islands
        for island in self.levels_data["islands"]:
            self._draw_island(surface, island)

        # Level panel for selected island
        if self._selected_island:
            self._draw_level_panel(surface)

        # XP bar
        draw_xp_bar(surface, 180, 28, 460, 24,
                     self.progress["player_xp"],
                     self.progress["player_level"])

        # Buttons
        self._back_btn.draw(surface)
        self._badge_btn.draw(surface)

        # Title
        title = self._font_title.render("Kies een eiland!", True, TEXT_LIGHT)
        surface.blit(title, title.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 36)))

    # ------------------------------------------------------------------
    def _draw_bg(self, surface: pygame.Surface) -> None:
        # Ocean gradient
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(26 + t * 20)
            g = int(26 + t * 60)
            b = int(46 + t * 100)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Waves
        wave_color = (40, 100, 160, 80)
        for i in range(5):
            offset = math.sin(self._anim_t * 0.8 + i * 1.2) * 8
            y0 = 150 + i * 120 + int(offset)
            pts = []
            for x in range(0, SCREEN_WIDTH + 20, 20):
                wy = y0 + math.sin(x / 80 + self._anim_t + i) * 6
                pts.append((x, int(wy)))
            if len(pts) >= 2:
                pygame.draw.lines(surface, (50, 130, 200), False, pts, 2)

    def _draw_paths(self, surface: pygame.Surface) -> None:
        islands = self.levels_data["islands"]
        for i in range(len(islands) - 1):
            p1 = islands[i].get("position", [200, 400])
            p2 = islands[i + 1].get("position", [400, 400])
            unlocked = (islands[i + 1]["id"] in
                        self.progress.get("islands_unlocked", [1]))
            color = (200, 200, 100) if unlocked else (80, 80, 100)
            pygame.draw.line(surface, color,
                              (p1[0], p1[1]), (p2[0], p2[1]), 4)
            # Dots on path
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            for step in [0.25, 0.5, 0.75]:
                px = int(p1[0] + dx * step)
                py = int(p1[1] + dy * step)
                pygame.draw.circle(surface, color, (px, py), 5)

    def _draw_island(self, surface: pygame.Surface, island: dict) -> None:
        iid = island["id"]
        rect = self._island_rects[iid]
        unlocked = iid in self.progress.get("islands_unlocked", [1])
        color = _ISLAND_COLORS.get(iid, PRIMARY) if unlocked else LOCKED_COLOR
        sel = self._selected_island == iid
        hover = self._island_hover == iid

        cx, cy = rect.centerx, rect.centery
        r = 70

        # Shadow
        pygame.draw.circle(surface, (0, 0, 0, 80), (cx + 4, cy + 6), r)
        # Island circle
        if sel:
            pulse = int(math.sin(self._anim_t * 4) * 5)
            pygame.draw.circle(surface, color, (cx, cy), r + pulse)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), r + pulse, 3)
        elif hover and unlocked:
            pygame.draw.circle(surface, color, (cx, cy), r + 3)
        else:
            pygame.draw.circle(surface, color, (cx, cy), r)

        # Lock icon
        if not unlocked:
            lock_font = get_font(36, header=True)
            lock = lock_font.render("🔒", True, (160, 160, 180))
            surface.blit(lock, lock.get_rect(center=(cx, cy - 8)))
        else:
            # Count stars
            total_stars = self._island_stars(iid)
            total_lvls = len([l for isl in self.levels_data["islands"]
                               if isl["id"] == iid for l in isl["levels"]])
            if total_stars == total_lvls * 3:
                crown = get_font(28, header=True).render("👑", True, (255, 220, 0))
                surface.blit(crown, crown.get_rect(center=(cx, cy - r - 12)))

        # Island name
        name_font = self._font_island
        name_c = TEXT_LIGHT if unlocked else (120, 120, 140)
        name_s = name_font.render(island["name"], True, name_c)
        surface.blit(name_s, name_s.get_rect(center=(cx, cy + r + 18)))

        # Completed stars below name
        if unlocked:
            completed = sum(
                1 for lv in [l for isl in self.levels_data["islands"]
                              if isl["id"] == iid for l in isl["levels"]]
                if f"{iid}-{lv['id']}" in self.progress["levels_completed"]
            )
            total = len([l for isl in self.levels_data["islands"]
                         if isl["id"] == iid for l in isl["levels"]])
            prog_s = self._font_small.render(f"{completed}/{total} levels", True, TEXT_LIGHT)
            surface.blit(prog_s, prog_s.get_rect(center=(cx, cy + r + 36)))

    def _draw_level_panel(self, surface: pygame.Surface) -> None:
        island = next((i for i in self.levels_data["islands"]
                        if i["id"] == self._selected_island), None)
        if not island:
            return

        panel_w = 320
        panel_h = min(500, 80 + len(island["levels"]) * 90 + 20)
        pos = island.get("position", [200, 400])
        px = min(SCREEN_WIDTH - panel_w - 10, max(10, pos[0] - panel_w // 2))
        py = min(SCREEN_HEIGHT - panel_h - 10, max(70, pos[1] - panel_h // 2))

        # Panel background
        pygame.draw.rect(surface, PANEL_BG,
                          (px, py, panel_w, panel_h), border_radius=20)
        pygame.draw.rect(surface, _ISLAND_COLORS.get(self._selected_island, PRIMARY),
                          (px, py, panel_w, panel_h), width=3, border_radius=20)

        title = self._font_island.render(island["name"], True,
                                          _ISLAND_COLORS.get(self._selected_island, PRIMARY))
        surface.blit(title, title.get_rect(center=(px + panel_w // 2, py + 26)))

        self._level_buttons[self._selected_island] = []
        for idx, lv in enumerate(island["levels"]):
            btn_y = py + 56 + idx * 82
            btn_rect = pygame.Rect(px + 16, btn_y, panel_w - 32, 70)

            unlocked = self._is_level_unlocked(self._selected_island, lv["id"])
            key = f"{self._selected_island}-{lv['id']}"
            completed = self.progress["levels_completed"].get(key, {})
            stars = completed.get("stars", 0)

            btn_color = SECONDARY if unlocked else LOCKED_COLOR
            if not unlocked:
                btn_color = (70, 70, 90)

            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=12)

            # Level title
            lv_font = self._font_level
            lv_text = f"{lv['id']}. {lv['title']}"
            lv_s = lv_font.render(lv_text, True,
                                   TEXT_LIGHT if unlocked else (100, 100, 120))
            surface.blit(lv_s, (btn_rect.x + 12, btn_rect.y + 8))

            if not unlocked:
                lock = get_font(20, header=True).render("🔒", True, (120, 120, 140))
                surface.blit(lock, (btn_rect.right - 34, btn_rect.y + 22))
            elif stars > 0:
                draw_stars(surface, btn_rect.right - 60, btn_rect.y + 48,
                            stars, 3, size=12, gap=4)
            else:
                new_s = self._font_small.render("Nieuw!", True, PRIMARY)
                surface.blit(new_s, (btn_rect.x + 12, btn_rect.y + 40))

            self._level_buttons[self._selected_island].append((btn_rect, lv))

    def _is_level_unlocked(self, island_id: int, level_id: int) -> bool:
        if level_id == 1:
            return True
        prev_key = f"{island_id}-{level_id - 1}"
        return prev_key in self.progress["levels_completed"]

    def _island_stars(self, island_id: int) -> int:
        return sum(
            self.progress["levels_completed"].get(
                f"{island_id}-{lv['id']}", {}).get("stars", 0)
            for isl in self.levels_data["islands"]
            if isl["id"] == island_id
            for lv in isl["levels"]
        )
