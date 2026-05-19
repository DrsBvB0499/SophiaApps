import json
import os

# When frozen by PyInstaller the writable data dir is next to the .exe,
# injected via CODEAAP_DATA_DIR before this module is first imported.
_DATA_DIR     = os.environ.get("CODEAAP_DATA_DIR", "data")
PROGRESS_PATH = os.path.join(_DATA_DIR, "progress.json")

DEFAULT_PROGRESS = {
    "player_name": "",
    "player_xp": 0,
    "player_level": 1,
    "levels_completed": {},
    "badges_earned": [],
    "islands_unlocked": [1],
}


def load_progress() -> dict:
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(PROGRESS_PATH):
        save_progress(DEFAULT_PROGRESS.copy())
        return DEFAULT_PROGRESS.copy()
    try:
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, val in DEFAULT_PROGRESS.items():
            data.setdefault(key, val)
        return data
    except (json.JSONDecodeError, OSError):
        return DEFAULT_PROGRESS.copy()


def save_progress(progress: dict) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def load_levels() -> dict:
    # levels.json is a bundled read-only asset; cwd is set to the bundle dir.
    path = os.path.join("data", "levels.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def complete_level(progress: dict, island_id: int, level_id: int,
                   stars: int, xp: int, levels_data: dict) -> list[str]:
    """Update progress after completing a level. Returns list of newly earned badge IDs."""
    key = f"{island_id}-{level_id}"
    prev = progress["levels_completed"].get(key, {})
    prev_stars = prev.get("stars", 0)

    if stars > prev_stars:
        progress["levels_completed"][key] = {"stars": stars, "xp_earned": xp}
        # Only add XP for improvement
        bonus_xp = xp if prev_stars == 0 else max(0, xp - prev.get("xp_earned", 0))
        progress["player_xp"] += bonus_xp

    # Recalculate player level
    from src.config import XP_PER_LEVEL, MAX_PLAYER_LEVEL
    new_level = min(MAX_PLAYER_LEVEL,
                    1 + progress["player_xp"] // XP_PER_LEVEL)
    progress["player_level"] = new_level

    # Unlock next level / island
    _unlock_next(progress, island_id, level_id, levels_data)

    new_badges = _check_badges(progress, island_id, level_id, stars, levels_data)
    save_progress(progress)
    return new_badges


def _unlock_next(progress: dict, island_id: int, level_id: int,
                 levels_data: dict) -> None:
    islands = levels_data["islands"]
    island = next((i for i in islands if i["id"] == island_id), None)
    if not island:
        return

    level_ids = [lv["id"] for lv in island["levels"]]
    if level_id < max(level_ids):
        pass  # next level on same island already unlocked implicitly

    # Unlock next island when all levels of current island are done
    completed_keys = set(progress["levels_completed"].keys())
    island_keys = {f"{island_id}-{lid}" for lid in level_ids}
    if island_keys.issubset(completed_keys):
        next_island = island_id + 1
        if next_island not in progress["islands_unlocked"]:
            progress["islands_unlocked"].append(next_island)


def _check_badges(progress: dict, island_id: int, level_id: int,
                  stars: int, levels_data: dict) -> list[str]:
    earned = set(progress["badges_earned"])
    new_badges: list[str] = []

    def earn(badge_id: str) -> None:
        if badge_id not in earned:
            earned.add(badge_id)
            new_badges.append(badge_id)

    total_completed = len(progress["levels_completed"])
    if total_completed >= 1:
        earn("first_win")

    if stars == 3:
        earn("no_mistakes")

    # Island 1 complete
    islands = levels_data["islands"]
    island = next((i for i in islands if i["id"] == island_id), None)
    if island:
        level_ids = [lv["id"] for lv in island["levels"]]
        completed_keys = set(progress["levels_completed"].keys())
        island_keys = {f"{island_id}-{lid}" for lid in level_ids}
        if island_keys.issubset(completed_keys):
            earn(f"island_{island_id}")

    if 2 in progress["islands_unlocked"]:
        earn("explorer")

    # streak_3: last 3 completed levels all 3-star
    all_completed = list(progress["levels_completed"].values())
    if len(all_completed) >= 3:
        last3 = all_completed[-3:]
        if all(lv.get("stars", 0) == 3 for lv in last3):
            earn("streak_3")

    # bug_finder: 5 type-C levels done
    type_c_done = sum(
        1 for isl in islands
        for lv in isl["levels"]
        if lv.get("type") == "debug"
        and f"{isl['id']}-{lv['id']}" in completed_keys
    )
    if type_c_done >= 5:
        earn("bug_finder")

    # loop_master: any type-D done
    type_d_done = any(
        f"{isl['id']}-{lv['id']}" in completed_keys
        for isl in islands
        for lv in isl["levels"]
        if lv.get("type") == "loop"
    )
    if type_d_done:
        earn("loop_master")

    # collector: 5 badges
    if len(earned) >= 5:
        earn("collector")

    # champion: all islands complete
    all_island_ids = [i["id"] for i in islands]
    if all(iid in progress["islands_unlocked"] for iid in all_island_ids):
        all_keys = {f"{i['id']}-{lv['id']}"
                    for i in islands for lv in i["levels"]}
        if all_keys.issubset(completed_keys):
            earn("champion")

    progress["badges_earned"] = list(earned)
    return new_badges
