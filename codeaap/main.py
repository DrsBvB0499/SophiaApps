"""CodeAap — main entry point."""
import os
import sys

# Ensure working directory is the project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from src.save import load_progress, load_levels, complete_level
from src import sounds

# ------------------------------------------------------------------ #
#  Scene imports                                                       #
# ------------------------------------------------------------------ #
from src.scenes.menu        import MenuScene
from src.scenes.world_map   import WorldMapScene
from src.scenes.level       import LevelScene
from src.scenes.reward      import RewardScene
from src.scenes.achievements import AchievementsScene


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    sounds.init_sounds()

    progress    = load_progress()
    levels_data = load_levels()

    # Scene state
    scene_name = "menu"
    scene = MenuScene(progress)

    # Pending level info (island_dict, level_dict) for world_map → level
    _pending_island: dict | None = None
    _pending_level:  dict | None = None
    _pending_result: dict | None = None
    _pending_new_badges: list   = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # ---- Events ------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Escape from any scene → menu
                if scene_name != "menu":
                    scene_name = "menu"
                    scene = MenuScene(progress)
                else:
                    running = False
            else:
                scene.handle_event(event)

        # ---- Update ------------------------------------------------ #
        scene.update(dt)

        # ---- Draw -------------------------------------------------- #
        scene.draw(screen)
        pygame.display.flip()

        # ---- Scene transitions ------------------------------------- #
        next_s = scene.next_scene()
        if not next_s:
            continue

        # -- FROM menu --
        if scene_name == "menu":
            progress = scene.progress        # capture name update
            if next_s == "world_map":
                scene_name = "world_map"
                scene = WorldMapScene(progress, levels_data)
            elif next_s == "achievements":
                scene_name = "achievements"
                scene = AchievementsScene(progress)

        # -- FROM world_map --
        elif scene_name == "world_map":
            if next_s == "menu":
                scene_name = "menu"
                scene = MenuScene(progress)
            elif next_s == "achievements":
                scene_name = "achievements"
                scene = AchievementsScene(progress)
            elif next_s == "level":
                info = scene.next_level_info()
                if info:
                    island_id, lv = info
                    _pending_island = next(
                        (i for i in levels_data["islands"] if i["id"] == island_id),
                        None)
                    _pending_level = lv
                    scene_name = "level"
                    scene = LevelScene(_pending_island, _pending_level, progress)

        # -- FROM level --
        elif scene_name == "level":
            if next_s == "world_map":
                scene_name = "world_map"
                scene = WorldMapScene(progress, levels_data)
            elif next_s == "reward":
                result = scene.get_result()
                if result:
                    prev_xp    = progress["player_xp"]
                    prev_level = progress["player_level"]
                    new_badges = complete_level(
                        progress,
                        result["island_id"],
                        result["level_id"],
                        result["stars"],
                        result["xp"],
                        levels_data,
                    )
                    scene_name = "reward"
                    scene = RewardScene(
                        result, new_badges, prev_xp, prev_level,
                        progress, _pending_island, _pending_level,
                    )

        # -- FROM reward --
        elif scene_name == "reward":
            if next_s == "world_map":
                scene_name = "world_map"
                scene = WorldMapScene(progress, levels_data)
            elif next_s == "level_next":
                info = scene.next_level_info()
                if info:
                    _pending_island, _pending_level = info
                    scene_name = "level"
                    scene = LevelScene(_pending_island, _pending_level, progress)
                else:
                    scene_name = "world_map"
                    scene = WorldMapScene(progress, levels_data)

        # -- FROM achievements --
        elif scene_name == "achievements":
            if next_s == "menu":
                scene_name = "menu"
                scene = MenuScene(progress)
            elif next_s == "world_map":
                scene_name = "world_map"
                scene = WorldMapScene(progress, levels_data)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
