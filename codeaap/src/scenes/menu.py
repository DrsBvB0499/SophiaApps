import pygame
import math
from src.config import (BG_COLOR, PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT,
                         TEXT_DARK, SCREEN_WIDTH, SCREEN_HEIGHT,
                         PANEL_BG, PANEL_BORDER, get_font)
from src.components.button import Button
from src.components.character import Character
from src import sounds


class MenuScene:
    def __init__(self, progress: dict):
        self.progress = progress
        self._next_scene: str | None = None
        self._name_input_active = not bool(progress.get("player_name"))

        self._input_text = progress.get("player_name", "")
        self._cursor_blink = 0.0
        self._cursor_visible = True

        self._ape = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, scale=1.8)
        self._ape_bounce = 0.0

        self._play_btn  = Button(SCREEN_WIDTH // 2 - 140, 530, 280, 80,
                                  "Spelen", SECONDARY, TEXT_DARK, 38)
        self._badge_btn = Button(SCREEN_WIDTH // 2 - 140, 630, 280, 70,
                                  "Badges", PRIMARY, TEXT_DARK, 32)
        self._confirm_btn = Button(SCREEN_WIDTH // 2 - 100, 480, 200, 64,
                                    "OK!", SECONDARY, TEXT_DARK, 34)

        self._font_logo  = get_font(72, header=True)
        self._font_sub   = get_font(28)
        self._font_input = get_font(32, header=True)

        self._particles: list[dict] = []
        self._spawn_particles()

    # ------------------------------------------------------------------
    def next_scene(self) -> str | None:
        s = self._next_scene
        self._next_scene = None
        return s

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self._name_input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self._input_text.strip():
                    self._confirm_name()
                elif event.key == pygame.K_BACKSPACE:
                    self._input_text = self._input_text[:-1]
                else:
                    if len(self._input_text) < 10 and event.unicode.isprintable():
                        self._input_text += event.unicode
            if self._confirm_btn.handle_event(event):
                if self._input_text.strip():
                    self._confirm_name()
        else:
            if self._play_btn.handle_event(event):
                sounds.play("click")
                self._next_scene = "world_map"
            if self._badge_btn.handle_event(event):
                sounds.play("click")
                self._next_scene = "achievements"

    def update(self, dt: float) -> None:
        self._ape.update(dt)
        self._ape_bounce += dt

        self._cursor_blink += dt
        if self._cursor_blink >= 0.5:
            self._cursor_blink = 0.0
            self._cursor_visible = not self._cursor_visible

        for p in self._particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            p["vy"] += 20 * dt
        self._particles = [p for p in self._particles if p["life"] > 0]
        if len(self._particles) < 15:
            self._spawn_particles()

        if self._name_input_active:
            self._confirm_btn.update(dt)
        else:
            self._play_btn.update(dt)
            self._badge_btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        self._draw_bg_stars(surface)

        # Floating particles
        for p in self._particles:
            alpha = min(255, int(p["life"] * 300))
            r = int(p["r"])
            if r > 0:
                pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), r)

        # Logo
        logo_y = 80
        logo_surf = self._font_logo.render("CodeAap", True, PRIMARY)
        logo_rect = logo_surf.get_rect(center=(SCREEN_WIDTH // 2, logo_y))
        surface.blit(logo_surf, logo_rect)

        # Sub-title
        sub = self._font_sub.render("Leer coderen, stap voor stap!", True, TEXT_LIGHT)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, logo_y + 60)))

        # Character
        bounce = math.sin(self._ape_bounce * 1.5) * 10
        self._ape.y = SCREEN_HEIGHT // 2 - 80 + bounce
        self._ape.draw(surface)

        if self._name_input_active:
            self._draw_name_input(surface)
        else:
            # Welcome
            name = self.progress.get("player_name", "")
            if name:
                welcome = self._font_sub.render(f"Hoi, {name}!", True, PRIMARY)
                surface.blit(welcome, welcome.get_rect(center=(SCREEN_WIDTH // 2, 420)))
            self._play_btn.draw(surface)
            self._badge_btn.draw(surface)

    # ------------------------------------------------------------------
    def _confirm_name(self) -> None:
        self.progress["player_name"] = self._input_text.strip()
        self._name_input_active = False
        sounds.play("correct")

    def _draw_name_input(self, surface: pygame.Surface) -> None:
        box_w, box_h = 400, 240
        box_x = SCREEN_WIDTH // 2 - box_w // 2
        box_y = 360
        pygame.draw.rect(surface, PANEL_BG, (box_x, box_y, box_w, box_h),
                          border_radius=20)
        pygame.draw.rect(surface, PRIMARY, (box_x, box_y, box_w, box_h),
                          width=3, border_radius=20)

        prompt = self._font_input.render("Wat is jouw naam?", True, TEXT_LIGHT)
        surface.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, box_y + 36)))

        # Input field
        field_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, box_y + 70, 320, 56)
        pygame.draw.rect(surface, (60, 60, 100), field_rect, border_radius=12)
        pygame.draw.rect(surface, PRIMARY, field_rect, width=2, border_radius=12)

        text_show = self._input_text
        if self._cursor_visible:
            text_show += "|"
        t_surf = self._font_input.render(text_show, True, TEXT_LIGHT)
        surface.blit(t_surf, t_surf.get_rect(center=field_rect.center))

        self._confirm_btn.draw(surface)

    def _spawn_particles(self) -> None:
        import random
        colors = [PRIMARY, SECONDARY, ACCENT, (100, 180, 255)]
        for _ in range(5):
            self._particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(-20, SCREEN_HEIGHT * 0.4),
                "vx": random.uniform(-20, 20),
                "vy": random.uniform(-10, 10),
                "r": random.uniform(3, 8),
                "life": random.uniform(2, 5),
                "color": random.choice(colors),
            })

    def _draw_bg_stars(self, surface: pygame.Surface) -> None:
        import random
        rng = random.Random(42)
        for _ in range(60):
            x = rng.randint(0, SCREEN_WIDTH)
            y = rng.randint(0, SCREEN_HEIGHT)
            r = rng.randint(1, 3)
            alpha = rng.randint(80, 200)
            pygame.draw.circle(surface, (alpha, alpha, alpha + 20), (x, y), r)
