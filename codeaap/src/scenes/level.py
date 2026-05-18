import pygame
import math
import time
from src.config import (BG_COLOR, PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT,
                         TEXT_DARK, SCREEN_WIDTH, SCREEN_HEIGHT,
                         PANEL_BG, PANEL_BORDER, LOCKED_COLOR,
                         BLOCK_COLORS, get_font)
from src.components.button import Button
from src.components.code_block import CodeBlock
from src.components.character import Character
from src import sounds

# ── Layout constants ────────────────────────────────────────────────────────
_GAME_Y      = 148          # top of the character-area panel
_GAME_H      = 200          # height  →  panel bottom = 348
_GAME_BOTTOM = _GAME_Y + _GAME_H          # 348
_GROUND_Y    = _GAME_BOTTOM - 20          # 328  (grass line)
_CHAR_Y      = _GAME_BOTTOM - 28          # 320  (feet position)
_TARGET_X    = SCREEN_WIDTH - 100
_TARGET_Y    = _GROUND_Y - 22

_UI_Y        = _GAME_BOTTOM + 14          # 362  (level-UI starts here)
_RUN_BTN_Y   = SCREEN_HEIGHT - 76         # 692


class LevelScene:
    def __init__(self, island: dict, level: dict, progress: dict):
        self.island   = island
        self.level    = level
        self.progress = progress

        self._next_scene: str | None = None
        self._result: dict | None = None

        self._mistakes = 0
        self._start_time = time.time()

        self._font_title  = get_font(28, header=True)
        self._font_instr  = get_font(24)
        self._font_block  = get_font(22, header=True)
        self._font_small  = get_font(18)

        self._back_btn = Button(16, 16, 130, 52, "← Terug", PANEL_BG, TEXT_LIGHT, 22)
        self._run_btn  = Button(SCREEN_WIDTH // 2 - 120, _RUN_BTN_Y,
                                 240, 60, "Uitvoeren!", SECONDARY, TEXT_DARK, 30)

        self._character = Character(180, _CHAR_Y, scale=1.4)

        # Feedback
        self._feedback: str = ""
        self._feedback_timer = 0.0
        self._shake_offset   = 0

        # Animation
        self._running  = False
        self._run_step_duration = 0.55

        self._type = level.get("type", "sequence")
        self._init_type()

    # ------------------------------------------------------------------
    def next_scene(self) -> str | None:
        s = self._next_scene
        self._next_scene = None
        return s

    def get_result(self) -> dict | None:
        return self._result

    # ------------------------------------------------------------------
    def _init_type(self) -> None:
        lv = self.level
        t  = self._type

        if t == "sequence":
            self._available: list[str]     = list(lv["available_blocks"])
            self._program:   list[str]     = []
            self._avail_blocks:   list[CodeBlock] = []
            self._program_blocks: list[CodeBlock] = []
            self._rebuild_avail_blocks()

        elif t == "choice":
            self._prefix   = list(lv.get("program_prefix", []))
            self._suffix   = list(lv.get("program_suffix", []))
            self._options  = list(lv["options"])
            self._correct  = lv["correct_block"]
            self._choice_buttons: list[Button] = []
            self._answered = False
            self._build_choice_buttons()

        elif t == "debug":
            self._debug_program = list(lv["program"])
            self._wrong_idx     = lv["wrong_index"]
            self._debug_blocks: list[CodeBlock] = []
            self._answered      = False
            self._build_debug_blocks()

        elif t == "loop":
            self._base_block_label = lv["base_block"]
            self._correct_count    = lv["correct_count"]
            self._selected_count   = 1
            self._answered         = False
            self._count_buttons: list[Button] = []
            self._build_loop_ui()

    # ------------------------------------------------------------------
    # Sequence helpers
    # ------------------------------------------------------------------
    def _rebuild_avail_blocks(self) -> None:
        self._avail_blocks.clear()
        x, y0 = 60, _UI_Y + 106        # below program zone + label
        gap = 10
        for i, label in enumerate(self._available):
            cb = CodeBlock(x, y0, label, i % len(BLOCK_COLORS))
            x += cb.base_rect.width + gap
            if x > SCREEN_WIDTH - 160:
                x = 60
                y0 += CodeBlock.HEIGHT + gap
            self._avail_blocks.append(cb)

    def _rebuild_program_blocks(self) -> None:
        self._program_blocks.clear()
        x, y0 = 60, _UI_Y + 22         # inside the program zone panel
        gap = 10
        for i, label in enumerate(self._program):
            cb = CodeBlock(x, y0, label, (i + 3) % len(BLOCK_COLORS))
            x += cb.base_rect.width + gap
            self._program_blocks.append(cb)

    # ------------------------------------------------------------------
    # Choice helpers
    # ------------------------------------------------------------------
    def _build_choice_buttons(self) -> None:
        self._choice_buttons.clear()
        bw, bh = 340, 68
        cols, gap_x, gap_y = 2, 20, 14
        total_w  = cols * bw + (cols - 1) * gap_x
        start_x  = SCREEN_WIDTH // 2 - total_w // 2
        start_y  = _UI_Y + 108          # below the partial program display
        colors   = [SECONDARY, ACCENT, (100, 180, 255), (200, 100, 200)]
        for i, opt in enumerate(self._options):
            col = i % cols
            row = i // cols
            btn = Button(start_x + col * (bw + gap_x),
                          start_y + row * (bh + gap_y),
                          bw, bh, opt, colors[i % len(colors)], TEXT_DARK, 24)
            self._choice_buttons.append(btn)

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------
    def _build_debug_blocks(self) -> None:
        self._debug_blocks.clear()
        x, y0 = 60, _UI_Y + 38
        gap = 12
        for i, label in enumerate(self._debug_program):
            cb = CodeBlock(x, y0, label, i % len(BLOCK_COLORS))
            x += cb.base_rect.width + gap
            self._debug_blocks.append(cb)

    # ------------------------------------------------------------------
    # Loop helpers
    # ------------------------------------------------------------------
    def _build_loop_ui(self) -> None:
        self._count_buttons.clear()
        bw, bh = 84, 84
        start_x = 180
        btn_y   = _UI_Y + 80
        for n in range(1, 6):
            btn = Button(start_x + (n - 1) * (bw + 14),
                          btn_y, bw, bh, str(n), SECONDARY, TEXT_DARK, 34)
            self._count_buttons.append(btn)

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self._running:
            return
        if self._back_btn.handle_event(event):
            sounds.play("click")
            self._next_scene = "world_map"
            return

        if self._type == "sequence":
            self._handle_sequence_event(event)
        elif self._type == "choice":
            self._handle_choice_event(event)
        elif self._type == "debug":
            self._handle_debug_event(event)
        elif self._type == "loop":
            self._handle_loop_event(event)

    def _handle_sequence_event(self, event: pygame.event.Event) -> None:
        for cb in self._avail_blocks:
            if cb.handle_event(event):
                sounds.play("click")
                self._program.append(cb.label)
                self._available.remove(cb.label)
                self._rebuild_avail_blocks()
                self._rebuild_program_blocks()
                return
        for cb in self._program_blocks:
            if cb.handle_event(event):
                sounds.play("click")
                self._available.append(cb.label)
                self._program.remove(cb.label)
                self._rebuild_avail_blocks()
                self._rebuild_program_blocks()
                return
        if self._run_btn.handle_event(event):
            self._check_sequence()

    def _handle_choice_event(self, event: pygame.event.Event) -> None:
        if self._answered:
            return
        for i, btn in enumerate(self._choice_buttons):
            if btn.handle_event(event):
                if self._options[i] == self._correct:
                    self._show_feedback("correct")
                    self._start_animation()
                else:
                    self._mistakes += 1
                    self._show_feedback("wrong")
                self._answered = True
                return

    def _handle_debug_event(self, event: pygame.event.Event) -> None:
        if self._answered:
            return
        for i, cb in enumerate(self._debug_blocks):
            if cb.handle_event(event):
                if i == self._wrong_idx:
                    self._show_feedback("correct")
                    self._start_animation()
                else:
                    self._mistakes += 1
                    self._show_feedback("wrong")
                    cb.color = (255, 80, 80)
                self._answered = True
                return

    def _handle_loop_event(self, event: pygame.event.Event) -> None:
        for i, btn in enumerate(self._count_buttons):
            if btn.handle_event(event):
                self._selected_count = i + 1
                sounds.play("click")
                return
        if self._run_btn.handle_event(event):
            if self._selected_count == self._correct_count:
                self._show_feedback("correct")
                self._start_animation()
            else:
                self._mistakes += 1
                self._show_feedback("wrong")

    # ------------------------------------------------------------------
    def _check_sequence(self) -> None:
        if self._program == self.level["correct_sequence"]:
            self._show_feedback("correct")
            self._start_animation()
        else:
            self._mistakes += 1
            self._show_feedback("wrong")

    def _show_feedback(self, kind: str) -> None:
        self._feedback       = kind
        self._feedback_timer = 1.2
        if kind == "correct":
            sounds.play("correct")
        else:
            sounds.play("wrong")
            self._shake_offset = 12

    def _start_animation(self) -> None:
        self._running = True
        self._character.reset_position(180, _CHAR_Y)
        for action in self.level.get("character_actions", []):
            self._character.queue_action(action, self._run_step_duration)

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        self._back_btn.update(dt)
        self._run_btn.update(dt)
        self._character.update(dt)

        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback == "wrong":
                self._shake_offset = int(math.sin(self._feedback_timer * 40) * 10)
            if self._feedback_timer <= 0:
                self._feedback     = ""
                self._shake_offset = 0

        if self._type == "sequence":
            for cb in self._avail_blocks + self._program_blocks:
                cb.update(dt)
        elif self._type == "choice":
            for btn in self._choice_buttons:
                btn.update(dt)
        elif self._type == "debug":
            for cb in self._debug_blocks:
                cb.update(dt)
        elif self._type == "loop":
            for btn in self._count_buttons:
                btn.update(dt)

        if self._running and not self._character.is_busy():
            self._running = False
            self._finish_level()

    def _finish_level(self) -> None:
        elapsed = time.time() - self._start_time
        stars   = self._calc_stars()
        xp_base = self.level.get("xp", 50)
        xp = xp_base if stars == 3 else (xp_base * 2 // 3 if stars == 2 else xp_base // 2)
        self._result = {
            "island_id": self.island["id"],
            "level_id":  self.level["id"],
            "stars":     stars,
            "xp":        xp,
            "time":      elapsed,
            "mistakes":  self._mistakes,
        }
        self._next_scene = "reward"

    def _calc_stars(self) -> int:
        thresh = self.level.get("star_thresholds", {"3": 0, "2": 1, "1": 2})
        m = self._mistakes
        if m <= int(thresh.get("3", 0)):
            return 3
        if m <= int(thresh.get("2", 1)):
            return 2
        return 1

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        self._draw_bg(surface)
        self._draw_header(surface)
        self._draw_instruction(surface)
        self._draw_game_area(surface)

        # Level-type UI is drawn AFTER game area so blocks appear on top
        if self._type == "sequence":
            self._draw_sequence(surface)
        elif self._type == "choice":
            self._draw_choice(surface)
        elif self._type == "debug":
            self._draw_debug(surface)
        elif self._type == "loop":
            self._draw_loop(surface)

        if self._feedback:
            self._draw_feedback(surface)

        self._back_btn.draw(surface)

    # ------------------------------------------------------------------
    def _draw_bg(self, surface: pygame.Surface) -> None:
        import random
        rng = random.Random(99)
        for _ in range(40):
            x = rng.randint(0, SCREEN_WIDTH)
            y = rng.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(surface, (60, 60, 90),
                                (x, y), rng.randint(1, 2))

    def _draw_header(self, surface: pygame.Surface) -> None:
        isl_color = tuple(
            int(self.island.get("color", "#F7B731").lstrip("#")[i:i+2], 16)
            for i in (0, 2, 4)
        )
        surface.blit(self._font_small.render(self.island["name"], True, isl_color),
                      (170, 16))
        surface.blit(self._font_title.render(self.level["title"], True, TEXT_LIGHT),
                      (170, 34))

    def _draw_instruction(self, surface: pygame.Surface) -> None:
        instr    = self.level.get("instruction", "")
        panel_w  = SCREEN_WIDTH - 40
        panel_rect = pygame.Rect(20, 80, panel_w, 58)
        pygame.draw.rect(surface, PANEL_BG,  panel_rect, border_radius=14)
        pygame.draw.rect(surface, PRIMARY,   panel_rect, width=2, border_radius=14)

        words = instr.split()
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            if self._font_instr.size(test)[0] < panel_w - 40:
                line = test
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        for i, ln in enumerate(lines[:2]):
            surface.blit(self._font_instr.render(ln, True, TEXT_LIGHT),
                          (36, 88 + i * 28))

    def _draw_game_area(self, surface: pygame.Surface) -> None:
        area_rect = pygame.Rect(20, _GAME_Y, SCREEN_WIDTH - 40, _GAME_H)
        pygame.draw.rect(surface, PANEL_BG,    area_rect, border_radius=16)
        pygame.draw.rect(surface, PANEL_BORDER, area_rect, width=2, border_radius=16)

        # Grass ground line
        pygame.draw.line(surface, (80, 150, 70),
                          (area_rect.left + 10,  _GROUND_Y),
                          (area_rect.right - 10, _GROUND_Y), 3)

        self._draw_target(surface, _TARGET_X, _TARGET_Y)
        self._character.draw(surface)

    def _draw_target(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw the goal object as pure geometry — no emoji, works on all platforms."""
        iid = self.island["id"]
        if iid == 1:
            self._draw_banana(surface, x, y)
        elif iid == 2:
            self._draw_fish(surface, x, y)
        else:
            self._draw_snowflake(surface, x, y)

    @staticmethod
    def _draw_banana(surface: pygame.Surface, cx: int, cy: int) -> None:
        """Yellow crescent / banana shape."""
        peel  = (255, 220,  30)
        tip   = (200, 160,  10)
        # Draw arc as a series of thick circles along a curve
        for deg in range(25, 165, 8):
            rad = math.radians(deg)
            bx  = cx + int(math.cos(rad) * 24)
            by  = cy - int(math.sin(rad) * 20) + int(math.cos(rad * 1.8) * 6)
            pygame.draw.circle(surface, peel, (bx, by), 9)
        # Tips
        for deg in [25, 160]:
            rad = math.radians(deg)
            bx  = cx + int(math.cos(rad) * 24)
            by  = cy - int(math.sin(rad) * 20) + int(math.cos(rad * 1.8) * 6)
            pygame.draw.circle(surface, tip, (bx, by), 6)

    @staticmethod
    def _draw_fish(surface: pygame.Surface, cx: int, cy: int) -> None:
        """Simple blue fish shape."""
        col  = (60, 130, 220)
        col2 = (40, 100, 180)
        # Body ellipse
        pygame.draw.ellipse(surface, col,  (cx - 22, cy - 12, 36, 24))
        # Tail triangle
        pygame.draw.polygon(surface, col2,
                             [(cx - 20, cy),
                              (cx - 40, cy - 16),
                              (cx - 40, cy + 16)])
        # Eye
        pygame.draw.circle(surface, (240, 240, 240), (cx + 8,  cy - 4), 5)
        pygame.draw.circle(surface, (20,  20,  20),  (cx + 9,  cy - 4), 3)
        # Fin
        pygame.draw.polygon(surface, col2,
                             [(cx - 5, cy - 12), (cx + 10, cy - 22), (cx + 14, cy - 12)])

    @staticmethod
    def _draw_snowflake(surface: pygame.Surface, cx: int, cy: int) -> None:
        """Six-spoke snowflake."""
        col = (180, 220, 255)
        for i in range(6):
            angle  = math.radians(i * 60)
            ex     = cx + int(math.cos(angle) * 24)
            ey     = cy + int(math.sin(angle) * 24)
            pygame.draw.line(surface, col, (cx, cy), (ex, ey), 3)
            for sign in (-1, 1):
                mid_x  = cx + int(math.cos(angle) * 13)
                mid_y  = cy + int(math.sin(angle) * 13)
                ba     = angle + sign * math.pi / 3
                bx     = mid_x + int(math.cos(ba) * 9)
                by_    = mid_y + int(math.sin(ba) * 9)
                pygame.draw.line(surface, col, (mid_x, mid_y), (bx, by_), 2)
        pygame.draw.circle(surface, (220, 240, 255), (cx, cy), 5)

    # ------------------------------------------------------------------
    def _draw_sequence(self, surface: pygame.Surface) -> None:
        sx = self._shake_offset if self._feedback == "wrong" else 0

        # Program zone panel
        prog_rect = pygame.Rect(20 + sx, _UI_Y, SCREEN_WIDTH - 40, 82)
        pygame.draw.rect(surface, (35, 55, 80),  prog_rect, border_radius=12)
        pygame.draw.rect(surface, (80, 120, 160), prog_rect, width=2, border_radius=12)

        lbl = self._font_small.render("Jouw programma:", True, (150, 200, 255))
        surface.blit(lbl, (32 + sx, _UI_Y + 4))

        if not self._program:
            hint = self._font_small.render("Klik blokken hieronder om ze toe te voegen",
                                            True, (100, 120, 150))
            surface.blit(hint, hint.get_rect(
                center=(SCREEN_WIDTH // 2 + sx, _UI_Y + 46)))

        for cb in self._program_blocks:
            orig_x = cb.base_rect.x
            cb.base_rect.x += sx
            cb.draw(surface)
            cb.base_rect.x = orig_x

        # Available zone label
        avail_lbl = self._font_small.render("Beschikbare blokken:", True, (180, 180, 200))
        surface.blit(avail_lbl, (32, _UI_Y + 88))

        for cb in self._avail_blocks:
            cb.draw(surface)

        self._run_btn.draw(surface)

    def _draw_choice(self, surface: pygame.Surface) -> None:
        # Programme preview label
        lbl = self._font_small.render("Kies het juiste blok:", True, (180, 180, 200))
        surface.blit(lbl, (32, _UI_Y + 4))

        # Partial program with blank slot
        all_blocks = (self.level.get("program_prefix", []) +
                      ["___"] +
                      self.level.get("program_suffix", []))
        x, y0 = 32, _UI_Y + 30
        gap = 10
        for i, label in enumerate(all_blocks):
            if label == "___":
                slot_w = 140
                slot_r = pygame.Rect(x, y0, slot_w, CodeBlock.HEIGHT)
                slot_c = SECONDARY if self._answered else (80, 80, 120)
                pygame.draw.rect(surface, slot_c,   slot_r, border_radius=12)
                pygame.draw.rect(surface, PRIMARY,  slot_r, width=2, border_radius=12)
                q = self._font_block.render("?", True, PRIMARY)
                surface.blit(q, q.get_rect(center=slot_r.center))
                x += slot_w + gap
            else:
                cb = CodeBlock(x, y0, label, i % len(BLOCK_COLORS))
                cb.enabled = False
                cb.draw(surface)
                x += cb.base_rect.width + gap

        for btn in self._choice_buttons:
            btn.draw(surface)

    def _draw_debug(self, surface: pygame.Surface) -> None:
        lbl = self._font_small.render("Klik op het foute blok:", True, (255, 180, 180))
        surface.blit(lbl, (32, _UI_Y + 4))

        for i, cb in enumerate(self._debug_blocks):
            if self._answered and i == self._wrong_idx:
                orig = cb.color
                cb.color = (255, 80, 80)
                cb.draw(surface)
                cb.color = orig
            else:
                cb.draw(surface)

    def _draw_loop(self, surface: pygame.Surface) -> None:
        loop_y = _UI_Y + 4

        loop_lbl  = self._font_title.render("HERHAAL", True, PRIMARY)
        count_lbl = self._font_title.render(f"{self._selected_count} keer:", True, SECONDARY)
        surface.blit(loop_lbl,  (60, loop_y))
        surface.blit(count_lbl, (240, loop_y))

        base_cb = CodeBlock(460, loop_y - 4, self._base_block_label, 2)
        base_cb.enabled = False
        base_cb.draw(surface)

        cnt_hint = self._font_small.render("Kies het aantal herhalingen:", True, (180, 180, 200))
        surface.blit(cnt_hint, (60, _UI_Y + 56))

        for i, btn in enumerate(self._count_buttons):
            btn.color = PRIMARY if (i + 1 == self._selected_count) else SECONDARY
            btn.draw(surface)

        self._run_btn.draw(surface)

    def _draw_feedback(self, surface: pygame.Surface) -> None:
        if self._feedback == "correct":
            color, text = (32, 191, 107), "Goed zo!"
        else:
            color, text = (252, 92, 101), "Fout! Probeer opnieuw."

        banner = pygame.Rect(SCREEN_WIDTH // 2 - 230, SCREEN_HEIGHT // 2 - 40,
                              460, 80)
        pygame.draw.rect(surface, color, banner, border_radius=16)
        font = get_font(36, header=True)
        surface.blit(font.render(text, True, TEXT_LIGHT),
                      font.render(text, True, TEXT_LIGHT).get_rect(
                          center=banner.center))
