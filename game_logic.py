from __future__ import annotations

from config import CONFIG
from delayed import DelayedEvent
from enemies import spawn_random_enemy
from groups import ALL_ENEMIES
from players import spawn_player
from timers import Timer


def init_game_state():
    with Timer("Game state init"):
        for player_id in range(1, CONFIG.NUM_OF_PLAYERS + 1):
            spawn_player(player_id)

        while len(ALL_ENEMIES) < 5:
            spawn_random_enemy()

        DelayedEvent(
            lambda: spawn_random_enemy() if len(ALL_ENEMIES) < 5 else None,
            5000,
            repeat=True,
            name="spawn_asteroid",
        )
