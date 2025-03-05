from __future__ import annotations

import pygame as pg


class Config:
    SHOW_HP = "players"
    _SHOW_HP = ["none", "players", "all"]
    FPS = 1000
    _FPS = [1000, 120, 60, 30]
    WORLD_WIDTH = 1600
    WORLD_HEIGHT = 900
    NUM_OF_PLAYERS = 2
    _NUM_OF_PLAYERS = [1, 2, 3, 4]
    RESOLUTION = pg.display.list_modes()[0]
    _RESOLUTION = pg.display.list_modes()
    MODE = "pvp"
    _MODE = ["pvp", "coop", "all_dmg"]

    def bump_option(self, name: str):
        val = getattr(self, name)
        options: list = getattr(self, "_" + name)
        pos = options.index(val)
        new_val = options[(pos + 1) % len(options)]
        setattr(self, name, new_val)


CONFIG = Config()
