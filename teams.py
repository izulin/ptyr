from __future__ import annotations

from typing import TYPE_CHECKING

from config import CONFIG
from consts import BLUE, CYAN, GREEN, PURPLE, RED

if TYPE_CHECKING:
    from objects import Object


def check_teams(obj_a: Object, obj_b: Object) -> bool:
    if CONFIG.MODE == "all_dmg":
        return True
    else:
        return get_team(obj_a) != get_team(obj_b)


def get_team(obj: Object) -> int:
    from players import Player

    obj = obj.owner
    if CONFIG.MODE in ["pvp", "all_dmg"]:
        if isinstance(obj, Player):
            return obj.player_id
        else:
            return 4
    elif CONFIG.MODE == "coop":
        if isinstance(obj, Player):
            return 0
        else:
            return 4
    raise NotImplementedError


def get_team_color(obj: Object):
    return [GREEN, CYAN, BLUE, PURPLE, RED][get_team(obj)]
