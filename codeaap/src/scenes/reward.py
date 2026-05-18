import pygame
import math
import random
from src.config import (BG_COLOR, PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT,
                         TEXT_DARK, SCREEN_WIDTH, SCREEN_HEIGHT,
                         PANEL_BG, get_font)
from src.components.button import Button
from src.components.character import Character
from src.components.star_display import draw_stars
from src.components.badge import BADGE_DEFS
from src import sounds


class RewardScene:
    def __init__(self, result: dict, new_badges: list[str],
                 prev_xp: int, prev_level: int, progress: dict,
                 island: dict, level: dict):
        self.result = result
        self.new_badges = new_badges
        self.prev_xp = prev_xp
        self.prev_level = prev_level
        self.progress = progress
        self.island = island
        self.level = level

        self._next_scene: str | None = None
        self._font_big   = get_font(56, header=True)
        self._font_title = get_font(36, header=True)
        self._font_mid   = get_font(28)
        self._font_small = get_font(20)

        # Next level info
        island_levels = island.get("levels", [])
        current_idx = next((i for i, lv in enumerate(island_levels)
                             if lv["id"] == level["id"]), -1)
        self._has_next = current_idx >= 0 and current_idx + 1 < len(island_levels)
        self._next_level = (island_levels[current_idx + 1]
                             if self._has_next else None)

        next_txt = f"Volgend level →" if self._has_next else "Terug naar kaart"
        self._next_btn = Button(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT - 110,
                                 340, 72, next_txt, SECONDARY, TEXT_DARK, 30)
        self._map_btn  = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 110 + 80,
                                 280, 58, "← Terug naar kaart", PANEL_BG, TEXT_LIGHT, 22)

        self._character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, scale=1.6)
        self._character.queue_action("dance", 99.0)

        # Confetti
        self._confetti = self._make_confetti(80)
        self._confetti_t = 0.0
        self._confetti_done = False

        # Badge slide-in
        self._badge_idx = 0
        self._badge_t = 0.0
        self._badge_x_offset = SCREEN_WIDTH   # starts off-screen right

        # XP counter animation
        self._xp_display = float(prev_xp)
        self._xp_target  = float(progress["player_xp"])

        # Level-up
        self._levelup_shown = False
        self._levelup_t = 0.0

        sounds.play("win")

    # ------------------------------------------------------------------
    def next_scene(self) -> str | None:
        s = self._next_scene
        self._next_scene = None
        return s

    def next_level_info(self):
        if self._has_next:
            return (self.island, self._next_level)
        return None

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self._next_btn.handle_event(event):
            sounds.play("click")
            if self._has_next:
                self._next_scene = "level_next"
            else:
                self._next_scene = "world_map"
        if self._map_btn.handle_event(event) and self._has_next:
            sounds.play("click")
            self._next_scene = "world_map"

    def update(self, dt: float) -> None:
        self._next_btn.update(dt)
        self._map_btn.update(dt)
        self._character.update(dt)

        self._confetti_t += dt
        for p in self._confetti:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt + 60 * dt
            p["rot"] += p["rot_v"] * dt
            if p["y"] > SCREEN_HEIGHT + 20:
                p["y"] = -10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

        # XP fill animation
        if self._xp_display < self._xp_target:
            self._xp_display = min(self._xp_target,
                                    self._xp_display + 120 * dt)

        # Badge slide-in
        if self._badge_idx < len(self.new_badges):
            self._badge_t += dt
            if self._badge_t < 0.5:
                self._badge_x_offset = int(SCREEN_WIDTH * (1 - self._badge_t / 0.5))
            else:
                self._badge_x_offset = 0
            if self._badge_t > 2.5:
                self._badge_idx += 1
                self._badge_t = 0.0
                self._badge_x_offset = SCREEN_WIDTH
                if self._badge_idx < len(self.new_badges):
                    sounds.play("badge")

        # Level-up check
        if (self.progress["player_level"] > self.prev_level
                and not self._levelup_shown):
            self._levelup_shown = True
            self._levelup_t = 3.0

        if self._levelup_t > 0:
            self._levelup_t -= dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        self._draw_bg(surface)

        # Confetti
        for p in self._confetti:
            self._draw_confetti_piece(surface, p)

        # "Geweldig!" header
        big = self._font_big.render("Geweldig! 🎉", True, PRIMARY)
        surface.blit(big, big.get_rect(center=(SCREEN_WIDTH // 2, 90)))

        # Level title
        lt = self._font_title.render(self.level["title"], True, TEXT_LIGHT)
        surface.blit(lt, lt.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        # Stars
        draw_stars(surface, SCREEN_WIDTH // 2, 220,
                    self.result["stars"], 3, size=48, gap=16)

        # XP gained
        xp_gained = self.result["xp"]
        xp_s = self._font_mid.render(f"+{xp_gained} XP", True, SECONDARY)
        surface.blit(xp_s, xp_s.get_rect(center=(SCREEN_WIDTH // 2, 290)))

        # XP bar
        self._draw_xp_bar(surface)

        # Character
        self._character.draw(surface)

        # Badge
        if self._badge_idx < len(self.new_badges):
            self._draw_badge_popup(surface)

        # Level-up banner
        if self._levelup_t > 0:
            self._draw_levelup(surface)

        self._next_btn.draw(surface)
        if self._has_next:
            self._map_btn.draw(surface)

    # ------------------------------------------------------------------
    def _draw_bg(self, surface: pygame.Surface) -> None:
        import random as rng
        r = rng.Random(77)
        for _ in range(50):
            x = r.randint(0, SCREEN_WIDTH)
            y = r.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(surface, (50, 50, 80), (x, y), r.randint(1, 3))

    def _draw_xp_bar(self, surface: pygame.Surface) -> None:
        from src.config import XP_PER_LEVEL
        bx, by, bw, bh = SCREEN_WIDTH // 2 - 200, 316, 400, 20
        xp_in = int(self._xp_display) % XP_PER_LEVEL
        ratio = xp_in / XP_PER_LEVEL
        pygame.draw.rect(surface, (50, 50, 80), (bx, by, bw, bh), border_radius=8)
        if ratio > 0:
            pygame.draw.rect(surface, SECONDARY,
                              (bx, by, int(bw * ratio), bh), border_radius=8)
        pygame.draw.rect(surface, PRIMARY, (bx, by, bw, bh), width=2, border_radius=8)
        lbl = self._font_small.render(
            f"Level {self.progress['player_level']}  —  "
            f"{int(self._xp_display) % XP_PER_LEVEL}/{XP_PER_LEVEL} XP",
            True, TEXT_LIGHT)
        surface.blit(lbl, lbl.get_rect(center=(SCREEN_WIDTH // 2, by + bh + 14)))

    def _draw_badge_popup(self, surface: pygame.Surface) -> None:
        bid = self.new_badges[self._badge_idx]
        defn = BADGE_DEFS.get(bid, {})
        bw, bh = 380, 100
        bx = SCREEN_WIDTH // 2 - bw // 2 + self._badge_x_offset
        by = SCREEN_HEIGHT - 240
        pygame.draw.rect(surface, defn.get("color", PRIMARY),
                          (bx, by, bw, bh), border_radius=16)

        icon_s = get_font(36, header=True).render(defn.get("icon", "🏅"), True, TEXT_LIGHT)
        surface.blit(icon_s, (bx + 14, by + bh // 2 - icon_s.get_height() // 2))

        title_s = get_font(22, header=True).render(
            f"Badge: {defn.get('name', bid)}", True, TEXT_LIGHT)
        surface.blit(title_s, (bx + 64, by + 18))

        desc_s = get_font(16).render(defn.get("desc", ""), True, (220, 220, 240))
        surface.blit(desc_s, (bx + 64, by + 48))

    def _draw_levelup(self, surface: pygame.Surface) -> None:
        alpha = min(255, int(self._levelup_t * 160))
        banner = pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT // 2 - 50,
                              520, 100)
        s = pygame.Surface((520, 100), pygame.SRCALPHA)
        s.fill((255, 200, 0, alpha))
        surface.blit(s, banner.topleft)
        text = get_font(38, header=True).render(
            f"🎊 Level {self.progress['player_level']} bereikt!", True, TEXT_DARK)
        surface.blit(text, text.get_rect(center=banner.center))

    @staticmethod
    def _make_confetti(n: int) -> list[dict]:
        colors = [
            (247, 183, 49), (32, 191, 107), (252, 92, 101),
            (100, 180, 255), (200, 100, 255), (255, 150, 50),
        ]
        result = []
        for _ in range(n):
            result.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(-SCREEN_HEIGHT, 0),
                "vx": random.uniform(-40, 40),
                "vy": random.uniform(30, 80),
                "w": random.randint(8, 18),
                "h": random.randint(5, 12),
                "rot": random.uniform(0, 360),
                "rot_v": random.uniform(-180, 180),
                "color": random.choice(colors),
            })
        return result

    @staticmethod
    def _draw_confetti_piece(surface: pygame.Surface, p: dict) -> None:
        surf = pygame.Surface((p["w"], p["h"]), pygame.SRCALPHA)
        surf.fill(p["color"])
        rotated = pygame.transform.rotate(surf, p["rot"])
        surface.blit(rotated, (int(p["x"]), int(p["y"])))
