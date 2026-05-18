import pygame
from src.config import (PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT, TEXT_DARK,
                         PANEL_BG, BUTTON_RADIUS, get_font, LOCKED_COLOR)

BADGE_DEFS = {
    "first_win":  {"name": "Eerste stap!",    "desc": "Je eerste level gehaald",         "color": SECONDARY,  "icon": "⭐"},
    "no_mistakes":{"name": "Perfect!",         "desc": "Geen enkele fout gemaakt",         "color": PRIMARY,    "icon": "✨"},
    "island_1":   {"name": "Bananeneiland held","desc": "Alle levels van eiland 1 voltooid","color": (255,165,0),"icon": "🍌"},
    "island_2":   {"name": "Jungleheld",       "desc": "Alle levels van eiland 2 voltooid","color": (100,200,100),"icon":"🌿"},
    "island_3":   {"name": "IJsheld",          "desc": "Alle levels van eiland 3 voltooid","color": (100,180,255),"icon":"❄️"},
    "streak_3":   {"name": "Op dreef!",        "desc": "3 levels op rij zonder fouten",   "color": ACCENT,     "icon": "🔥"},
    "explorer":   {"name": "Ontdekker",        "desc": "Eiland 2 ontgrendeld",             "color": (80,200,255),"icon":"🗺️"},
    "bug_finder": {"name": "Bug vinder",       "desc": "5 debug-levels voltooid",          "color": (200,100,200),"icon":"🐛"},
    "loop_master":{"name": "Lus-meester",      "desc": "Eerste herhaling-level voltooid", "color": (255,150,50),"icon":"🔄"},
    "collector":  {"name": "Verzamelaar",      "desc": "5 badges behaald",                "color": (200,200,50),"icon":"🏅"},
    "champion":   {"name": "Kampioen",         "desc": "Alle eilanden voltooid",           "color": PRIMARY,    "icon":"🏆"},
    "speed_star": {"name": "Razendsnel",       "desc": "Level in minder dan 30 seconden", "color": ACCENT,     "icon":"⚡"},
}


class BadgeTile:
    SIZE = 120

    def __init__(self, x: int, y: int, badge_id: str, unlocked: bool):
        self.x = x
        self.y = y
        self.badge_id = badge_id
        self.unlocked = unlocked
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self._hover = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)

    def draw(self, surface: pygame.Surface) -> None:
        defn = BADGE_DEFS.get(self.badge_id, {})
        color = defn.get("color", PRIMARY) if self.unlocked else LOCKED_COLOR
        icon  = defn.get("icon", "?")
        name  = defn.get("name", self.badge_id)

        if self._hover and self.unlocked:
            color = tuple(min(255, c + 30) for c in color)

        pygame.draw.rect(surface, color, self.rect, border_radius=16)
        pygame.draw.rect(surface, (255, 255, 255, 80), self.rect,
                         width=2, border_radius=16)

        font_icon = get_font(36, header=True)
        font_name = get_font(14)

        if self.unlocked:
            icon_s = font_icon.render(icon, True, TEXT_LIGHT)
        else:
            icon_s = font_icon.render("?", True, (160, 160, 180))

        surface.blit(icon_s, icon_s.get_rect(
            center=(self.x + self.SIZE // 2, self.y + self.SIZE // 2 - 12)))

        label = name if self.unlocked else "???"
        name_s = font_name.render(label, True,
                                   TEXT_LIGHT if self.unlocked else (120, 120, 140))
        surface.blit(name_s, name_s.get_rect(
            center=(self.x + self.SIZE // 2, self.y + self.SIZE - 18)))
