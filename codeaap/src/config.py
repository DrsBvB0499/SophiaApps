import pygame

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "CodeAap - Leer Coderen"

# Colour palette
BG_COLOR       = (26, 26, 46)       # #1A1A2E  dark blue
PRIMARY        = (247, 183, 49)     # #F7B731  gold
SECONDARY      = (32, 191, 107)     # #20BF6B  green
ACCENT         = (252, 92, 101)     # #FC5C65  red/pink
TEXT_LIGHT     = (255, 255, 255)
TEXT_DARK      = (45, 52, 54)
PANEL_BG       = (40, 40, 70)
PANEL_BORDER   = (80, 80, 140)
LOCKED_COLOR   = (100, 100, 120)

BLOCK_COLORS = [
    (255, 107, 107),  # red
    (255, 183, 77),   # orange
    (102, 204, 102),  # green
    (77, 166, 255),   # blue
    (204, 102, 255),  # purple
]

STAR_COLOR    = (247, 183, 49)
STAR_EMPTY    = (80, 80, 100)

XP_PER_LEVEL  = 200
MAX_PLAYER_LEVEL = 10

BUTTON_RADIUS = 16
BUTTON_MIN_H  = 80

FONT_PATH_HEADER = "assets/fonts/FredokaOne-Regular.ttf"
FONT_PATH_BODY   = "assets/fonts/Nunito-Regular.ttf"

_font_cache: dict = {}


def get_font(size: int, bold: bool = False, header: bool = False) -> pygame.font.Font:
    key = (size, bold, header)
    if key not in _font_cache:
        path = FONT_PATH_HEADER if header else FONT_PATH_BODY
        try:
            _font_cache[key] = pygame.font.Font(path, size)
        except FileNotFoundError:
            import warnings
            warnings.warn(f"Font not found: {path}, falling back to system font")
            style = "arialbd" if bold else "arial"
            _font_cache[key] = pygame.font.SysFont(style, size)
    return _font_cache[key]
