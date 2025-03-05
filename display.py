from __future__ import annotations

import pygame as pg

from timers import Timer

with Timer("pg.init()"):
    pg.init()

from config import CONFIG


def set_mode():
    with Timer("pg.display.set_mode()"):
        pg.display.set_mode(
            CONFIG.RESOLUTION,
            flags=pg.FULLSCREEN | pg.SRCALPHA | pg.SCALED,
            vsync=1,
        )


set_mode()

DISPLAYSURF = pg.Surface((CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT), flags=pg.SRCALPHA)

ALL_CHANGES_DISPLAYSURF: list[pg.Rect] = []
