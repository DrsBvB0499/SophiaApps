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


class LevelScene:
    def __init__(self, island: dict, level: dict, progress: dict):
        self.island   = island
        self.level    = level
        self.progress = progress

        self._next_scene: str | None = None
        self._result: dict | None = None   # set when level done

        self._mistakes = 0
        self._start_time = time.time()

        self._font_title  = get_font(28, header=True)
        self._font_instr  = get_font(24)
        self._font_block  = get_font(22, header=True)
        self._font_small  = get_font(18)

        self._back_btn = Button(16, 16, 130, 52, "← Terug", PANEL_BG, TEXT_LIGHT, 22)
        self._run_btn  = Button(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 76,
                                 240, 60, "▶ Uitvoeren", SECONDARY, TEXT_DARK, 30)

        self._character = Character(200, 440, scale=1.4)

        # Feedback state
        self._feedback: str = ""          # "correct" | "wrong" | ""
        self._feedback_timer = 0.0
        self._shake_offset = 0

        # Animation running
        self._running = False
        self._run_step = 0
        self._run_timer = 0.0
        self._run_step_duration = 0.6

        # Level-type specific state
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
        t = self._type

        if t == "sequence":
            self._available = list(lv["available_blocks"])
            self._program: list[str] = []
            self._avail_blocks: list[CodeBlock] = []
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
            self._wrong_idx = lv["wrong_index"]
            self._debug_blocks: list[CodeBlock] = []
            self._answered = False
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
        x0, y0 = 60, 540
        gap = 10
        x = x0
        for i, label in enumerate(self._available):
            cb = CodeBlock(x, y0, label, i % len(BLOCK_COLORS))
            x += cb.base_rect.width + gap
            if x > SCREEN_WIDTH - 200:
                x = x0
                y0 += CodeBlock.HEIGHT + gap
            self._avail_blocks.append(cb)

    def _rebuild_program_blocks(self) -> None:
        self._program_blocks.clear()
        x0, y0 = 60, 460
        gap = 10
        x = x0
        for i, label in enumerate(self._program):
            cb = CodeBlock(x, y0, label, (i + 3) % len(BLOCK_COLORS))
            x += cb.base_rect.width + gap
            self._program_blocks.append(cb)

    # ------------------------------------------------------------------
    # Choice helpers
    # ------------------------------------------------------------------
    def _build_choice_buttons(self) -> None:
        self._choice_buttons.clear()
        bw, bh = 340, 64
        cols = 2
        gap_x, gap_y = 20, 16
        total_w = cols * bw + (cols - 1) * gap_x
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        start_y = 450
        colors = [SECONDARY, ACCENT, (100, 180, 255), (200, 100, 200)]
        for i, opt in enumerate(self._options):
            col = i % cols
            row = i // cols
            bx = start_x + col * (bw + gap_x)
            by = start_y + row * (bh + gap_y)
            btn = Button(bx, by, bw, bh, opt, colors[i % len(colors)],
                          TEXT_DARK, 24)
            self._choice_buttons.append(btn)

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------
    def _build_debug_blocks(self) -> None:
        self._debug_blocks.clear()
        x0, y0 = 60, 440
        gap = 12
        x = x0
        for i, label in enumerate(self._debug_program):
            cb = CodeBlock(x, y0, label, i % len(BLOCK_COLORS))
            x += cb.base_rect.width + gap
            self._debug_blocks.append(cb)

    # ------------------------------------------------------------------
    # Loop helpers
    # ------------------------------------------------------------------
    def _build_loop_ui(self) -> None:
        self._count_buttons.clear()
        for n in range(1, 6):
            bw, bh = 80, 80
            bx = 180 + (n - 1) * (bw + 16)
            by = 500
            btn = Button(bx, by, bw, bh, str(n), SECONDARY, TEXT_DARK, 32)
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
        # Click available block → add to program
        for cb in self._avail_blocks:
            if cb.handle_event(event):
                sounds.play("click")
                self._program.append(cb.label)
                self._available.remove(cb.label)
                self._rebuild_avail_blocks()
                self._rebuild_program_blocks()
                return

        # Click program block → remove (return to available)
        for cb in self._program_blocks:
            if cb.handle_event(event):
                sounds.play("click")
                self._available.append(cb.label)
                self._program.remove(cb.label)
                self._rebuild_avail_blocks()
                self._rebuild_program_blocks()
                return

        # Run button
        if self._run_btn.handle_event(event):
            self._check_sequence()

    def _handle_choice_event(self, event: pygame.event.Event) -> None:
        if self._answered:
            return
        for i, btn in enumerate(self._choice_buttons):
            if btn.handle_event(event):
                chosen = self._options[i]
                if chosen == self._correct:
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
        correct = self.level["correct_sequence"]
        if self._program == correct:
            self._show_feedback("correct")
            self._start_animation()
        else:
            self._mistakes += 1
            self._show_feedback("wrong")

    def _show_feedback(self, kind: str) -> None:
        self._feedback = kind
        self._feedback_timer = 1.0
        if kind == "correct":
            sounds.play("correct")
        else:
            sounds.play("wrong")
            self._shake_offset = 12

    def _start_animation(self) -> None:
        self._running = True
        self._run_step = 0
        self._run_timer = 0.0
        actions = self.level.get("character_actions", [])
        self._character.reset_position(200, 440)
        for action in actions:
            self._character.queue_action(action, self._run_step_duration)

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        self._back_btn.update(dt)
        self._run_btn.update(dt)
        self._character.update(dt)

        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback == "wrong" and self._shake_offset > 0:
                self._shake_offset = int(math.sin(self._feedback_timer * 40) * 10)
            if self._feedback_timer <= 0:
                self._feedback = ""
                self._shake_offset = 0

        if self._type == "sequence":
            for cb in self._avail_blocks:
                cb.update(dt)
            for cb in self._program_blocks:
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

        # Check if animation finished → go to reward
        if self._running and not self._character.is_busy():
            self._running = False
            self._finish_level()

    def _finish_level(self) -> None:
        elapsed = time.time() - self._start_time
        stars = self._calc_stars()
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

        # Header
        self._draw_header(surface)

        # Instructions
        self._draw_instruction(surface)

        # Game area (character)
        self._draw_game_area(surface)

        # Level-type UI
        if self._type == "sequence":
            self._draw_sequence(surface)
        elif self._type == "choice":
            self._draw_choice(surface)
        elif self._type == "debug":
            self._draw_debug(surface)
        elif self._type == "loop":
            self._draw_loop(surface)

        # Feedback banner
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
            r = rng.randint(1, 2)
            pygame.draw.circle(surface, (60, 60, 90), (x, y), r)

    def _draw_header(self, surface: pygame.Surface) -> None:
        isl_color = tuple(
            int(self.island.get("color", "#F7B731").lstrip("#")[i:i+2], 16)
            for i in (0, 2, 4)
        )
        island_s = self._font_small.render(self.island["name"], True, isl_color)
        surface.blit(island_s, (170, 16))

        title_s = self._font_title.render(self.level["title"], True, TEXT_LIGHT)
        surface.blit(title_s, (170, 34))

    def _draw_instruction(self, surface: pygame.Surface) -> None:
        instr = self.level.get("instruction", "")
        panel_w = SCREEN_WIDTH - 40
        panel_h = 56
        panel_rect = pygame.Rect(20, 80, panel_w, panel_h)
        pygame.draw.rect(surface, PANEL_BG, panel_rect, border_radius=14)
        pygame.draw.rect(surface, PRIMARY, panel_rect, width=2, border_radius=14)

        # Word-wrap simple
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
            s = self._font_instr.render(ln, True, TEXT_LIGHT)
            surface.blit(s, (36, 88 + i * 26))

    def _draw_game_area(self, surface: pygame.Surface) -> None:
        area_rect = pygame.Rect(20, 148, SCREEN_WIDTH - 40, 270)
        pygame.draw.rect(surface, PANEL_BG, area_rect, border_radius=16)
        pygame.draw.rect(surface, PANEL_BORDER, area_rect, width=2, border_radius=16)

        # Ground line
        ground_y = area_rect.bottom - 30
        pygame.draw.line(surface, (80, 130, 80),
                          (area_rect.left + 10, ground_y),
                          (area_rect.right - 10, ground_y), 3)

        # Target (banana/fish)
        target_x = area_rect.right - 80
        target_y = ground_y - 20
        self._draw_target(surface, target_x, target_y)

        self._character.draw(surface)

    def _draw_target(self, surface: pygame.Surface, x: int, y: int) -> None:
        font = get_font(40, header=True)
        target_icons = ["🍌", "🐟", "🍎"]
        icon = target_icons[(self.island["id"] - 1) % len(target_icons)]
        s = font.render(icon, True, PRIMARY)
        surface.blit(s, (x - s.get_width() // 2, y - s.get_height() // 2))

    def _draw_sequence(self, surface: pygame.Surface) -> None:
        sx = self._shake_offset if self._feedback == "wrong" else 0

        # Program zone
        prog_rect = pygame.Rect(20 + sx, 430, SCREEN_WIDTH - 40, 80)
        pygame.draw.rect(surface, (40, 60, 80), prog_rect, border_radius=12)
        pygame.draw.rect(surface, (80, 120, 160), prog_rect, width=2, border_radius=12)

        prog_label = self._font_small.render("Jouw programma:", True, (150, 200, 255))
        surface.blit(prog_label, (32 + sx, 434))

        if not self._program:
            hint = self._font_small.render("← Klik blokken hieronder om ze toe te voegen",
                                            True, (100, 120, 150))
            surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2 + sx, 475)))

        for cb in self._program_blocks:
            orig_x = cb.base_rect.x
            cb.base_rect.x += sx
            cb.draw(surface)
            cb.base_rect.x = orig_x

        # Available zone
        avail_label = self._font_small.render("Beschikbare blokken:", True, (180, 180, 200))
        surface.blit(avail_label, (32, 524))

        for cb in self._avail_blocks:
            cb.draw(surface)

        self._run_btn.draw(surface)

    def _draw_choice(self, surface: pygame.Surface) -> None:
        # Show the partial program
        all_blocks = (self.level.get("program_prefix", []) +
                      ["___"] +
                      self.level.get("program_suffix", []))
        x0, y0 = 60, 440
        gap = 10
        x = x0
        for i, label in enumerate(all_blocks):
            if label == "___":
                w = 140
                rect = pygame.Rect(x, y0, w, CodeBlock.HEIGHT)
                color = (80, 80, 120) if not self._answered else SECONDARY
                pygame.draw.rect(surface, color, rect, border_radius=12)
                pygame.draw.rect(surface, PRIMARY, rect, width=2, border_radius=12)
                q = self._font_block.render("?", True, PRIMARY)
                surface.blit(q, q.get_rect(center=rect.center))
                x += w + gap
            else:
                cb = CodeBlock(x, y0, label, i % len(BLOCK_COLORS))
                cb.enabled = False
                cb.draw(surface)
                x += cb.base_rect.width + gap

        opt_label = self._font_small.render("Kies het juiste blok:", True, (180, 180, 200))
        surface.blit(opt_label, (60, 420))

        for btn in self._choice_buttons:
            btn.draw(surface)

    def _draw_debug(self, surface: pygame.Surface) -> None:
        label = self._font_small.render("Klik op het foute blok:", True, (255, 180, 180))
        surface.blit(label, (32, 420))

        for i, cb in enumerate(self._debug_blocks):
            if self._answered and i == self._wrong_idx:
                orig_color = cb.color
                cb.color = (255, 80, 80)
                cb.draw(surface)
                cb.color = orig_color
            else:
                cb.draw(surface)

    def _draw_loop(self, surface: pygame.Surface) -> None:
        # Show: HERHAAL [ N ] KEER: [base_block]
        loop_y = 430
        loop_label = self._font_title.render("HERHAAL", True, PRIMARY)
        surface.blit(loop_label, (60, loop_y))

        # Count selector
        count_label = self._font_title.render(f"{self._selected_count} keer:", True, SECONDARY)
        surface.blit(count_label, (220, loop_y))

        base_cb = CodeBlock(440, loop_y - 4, self._base_block_label, 2)
        base_cb.enabled = False
        base_cb.draw(surface)

        cnt_lbl = self._font_small.render("Kies het aantal:", True, (180, 180, 200))
        surface.blit(cnt_lbl, (60, 486))

        for i, btn in enumerate(self._count_buttons):
            if i + 1 == self._selected_count:
                btn.color = PRIMARY
            else:
                btn.color = SECONDARY
            btn.draw(surface)

        self._run_btn.draw(surface)

    def _draw_feedback(self, surface: pygame.Surface) -> None:
        if self._feedback == "correct":
            color = (32, 191, 107, 200)
            text = "✓ Goed zo!"
            tc = (255, 255, 255)
        else:
            color = (252, 92, 101, 200)
            text = "✗ Probeer nog een keer!"
            tc = (255, 255, 255)

        banner = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 36,
                              440, 72)
        pygame.draw.rect(surface, color[:3], banner, border_radius=16)
        font = get_font(34, header=True)
        s = font.render(text, True, tc)
        surface.blit(s, s.get_rect(center=banner.center))
