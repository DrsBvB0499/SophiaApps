import pygame
import math
from src.config import PRIMARY, SECONDARY, ACCENT, TEXT_DARK


class Character:
    """CodeAap drawn with geometric shapes. Supports idle bounce and actions."""

    IDLE_FRAMES = 4
    IDLE_FPS = 8

    def __init__(self, x: int, y: int, scale: float = 1.0):
        self.x = float(x)
        self.y = float(y)
        self.scale = scale
        self._base_y = float(y)

        self._anim_timer = 0.0
        self._frame = 0
        self._bounce_offset = 0.0

        # Current action
        self._action: str = "idle"
        self._action_timer = 0.0
        self._action_duration = 0.0
        self._action_queue: list[tuple[str, float]] = []

        self._face_right = True
        self._move_vx = 0.0
        self._jump_vy = 0.0
        self._arm_raise = 0.0    # 0..1 for grab animation
        self._dance_t = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def queue_action(self, action: str, duration: float = 0.5) -> None:
        self._action_queue.append((action, duration))

    def is_busy(self) -> bool:
        return bool(self._action != "idle" or self._action_queue)

    def reset_position(self, x: int, y: int) -> None:
        self.x = float(x)
        self.y = float(y)
        self._base_y = float(y)
        self._action = "idle"
        self._action_queue.clear()

    def update(self, dt: float) -> None:
        # Idle bounce
        self._anim_timer += dt
        if self._anim_timer >= 1.0 / self.IDLE_FPS:
            self._anim_timer -= 1.0 / self.IDLE_FPS
            self._frame = (self._frame + 1) % self.IDLE_FRAMES

        idle_bounce_amp = 4 * self.scale
        self._bounce_offset = math.sin(self._frame * math.pi / 2) * idle_bounce_amp

        # Process action queue
        if self._action == "idle" and self._action_queue:
            self._action, self._action_duration = self._action_queue.pop(0)
            self._action_timer = 0.0
            self._setup_action(self._action)

        if self._action != "idle":
            self._action_timer += dt
            self._run_action(self._action, dt)
            if self._action_timer >= self._action_duration:
                self._finish_action(self._action)
                self._action = "idle"
                self._action_timer = 0.0

        # Dance
        if self._action == "idle":
            self._dance_t = 0.0
        else:
            self._dance_t += dt

    def draw(self, surface: pygame.Surface) -> None:
        s = self.scale
        bx = int(self.x)
        by = int(self.y + self._bounce_offset)

        if self._action == "jump":
            t = self._action_timer / max(self._action_duration, 0.001)
            jump_h = math.sin(t * math.pi) * 60 * s
            by -= int(jump_h)

        if self._action == "dance":
            dance_off = math.sin(self._dance_t * 8) * 6 * s
            by += int(dance_off)

        flip = not self._face_right
        self._draw_ape(surface, bx, by, s, flip)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _setup_action(self, action: str) -> None:
        if action == "move_right":
            self._face_right = True
        elif action == "move_left":
            self._face_right = False
        elif action == "grab":
            self._arm_raise = 0.0

    def _run_action(self, action: str, dt: float) -> None:
        t = self._action_timer / max(self._action_duration, 0.001)
        if action == "move_right":
            self.x += 80 * self.scale * dt
        elif action == "move_left":
            self.x -= 80 * self.scale * dt
        elif action == "grab":
            self._arm_raise = min(1.0, t * 2)

    def _finish_action(self, action: str) -> None:
        self._arm_raise = 0.0

    def _draw_ape(self, surface: pygame.Surface, cx: int, cy: int,
                  s: float, flip: bool) -> None:
        # Body
        body_color   = (139, 90, 43)
        face_color   = (210, 160, 100)
        dark_brown   = (90, 55, 20)
        eye_white    = (240, 240, 240)
        eye_pupil    = (30, 30, 30)
        ear_color    = (160, 110, 60)
        shirt_color  = PRIMARY
        belly_color  = (200, 150, 90)

        bw = int(38 * s)
        bh = int(44 * s)
        body_rect = pygame.Rect(cx - bw // 2, cy - bh, bw, bh)
        pygame.draw.ellipse(surface, body_color, body_rect)

        # Belly
        belly_r = pygame.Rect(cx - bw // 3, cy - bh + bh // 4,
                               bw * 2 // 3, bh // 2)
        pygame.draw.ellipse(surface, belly_color, belly_r)

        # Shirt stripe
        shirt_r = pygame.Rect(cx - bw // 2, cy - bh + bh // 2 - 4,
                               bw, int(14 * s))
        pygame.draw.rect(surface, shirt_color, shirt_r)

        # Head
        head_r = int(22 * s)
        head_cx = cx
        head_cy = cy - bh - head_r + int(6 * s)
        pygame.draw.circle(surface, body_color, (head_cx, head_cy), head_r)

        # Face plate
        face_r = int(16 * s)
        pygame.draw.circle(surface, face_color, (head_cx, head_cy + int(4 * s)), face_r)

        # Ears
        ear_r = int(9 * s)
        ex = int(14 * s)
        pygame.draw.circle(surface, ear_color, (head_cx - ex, head_cy), ear_r)
        pygame.draw.circle(surface, ear_color, (head_cx + ex, head_cy), ear_r)

        # Eyes
        eye_off = int(7 * s)
        eye_r = int(5 * s)
        for ex2 in [-eye_off, eye_off]:
            pygame.draw.circle(surface, eye_white,
                                (head_cx + ex2, head_cy - int(2 * s)), eye_r)
            pygame.draw.circle(surface, eye_pupil,
                                (head_cx + ex2 + (1 if not flip else -1),
                                 head_cy - int(2 * s)), int(3 * s))

        # Nose
        pygame.draw.circle(surface, dark_brown,
                            (head_cx, head_cy + int(5 * s)), int(3 * s))

        # Mouth (smile)
        mouth_rect = pygame.Rect(head_cx - int(7 * s), head_cy + int(6 * s),
                                  int(14 * s), int(8 * s))
        pygame.draw.arc(surface, dark_brown, mouth_rect,
                         math.pi, 2 * math.pi, int(2 * s))

        # Arms
        arm_len = int(26 * s)
        arm_y_top = cy - bh + int(12 * s)
        arm_w = int(10 * s)

        # Right arm (screen right)
        right_raise = int(self._arm_raise * 30 * s) if not flip else 0
        pygame.draw.ellipse(surface, body_color,
                             pygame.Rect(cx + bw // 2 - arm_w // 2,
                                         arm_y_top - right_raise,
                                         arm_w, arm_len))

        # Left arm
        left_raise = int(self._arm_raise * 30 * s) if flip else 0
        pygame.draw.ellipse(surface, body_color,
                             pygame.Rect(cx - bw // 2 - arm_w // 2,
                                         arm_y_top - left_raise,
                                         arm_w, arm_len))

        # Legs
        leg_w = int(12 * s)
        leg_h = int(30 * s)
        pygame.draw.ellipse(surface, dark_brown,
                             pygame.Rect(cx - bw // 4 - leg_w // 2,
                                         cy - leg_h // 2,
                                         leg_w, leg_h))
        pygame.draw.ellipse(surface, dark_brown,
                             pygame.Rect(cx + bw // 4 - leg_w // 2,
                                         cy - leg_h // 2,
                                         leg_w, leg_h))

        # Tail
        tail_start = (cx - bw // 2, cy - bh // 3)
        tail_cp    = (cx - int(50 * s), cy - bh // 2 - int(20 * s))
        tail_end   = (cx - int(35 * s), cy - bh - int(10 * s))
        self._draw_bezier(surface, dark_brown,
                          tail_start, tail_cp, tail_end, int(3 * s))

    @staticmethod
    def _draw_bezier(surface, color, p0, p1, p2, width):
        steps = 20
        pts = []
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
            pts.append((int(x), int(y)))
        if len(pts) >= 2:
            pygame.draw.lines(surface, color, False, pts, width)
