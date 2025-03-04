from __future__ import annotations

import pygame as pg

from config import CONFIG
from timers import Timer

with Timer("pg.init()"):
    pg.init()

sizes = pg.display.list_modes()

with Timer("pg.display.set_mode()"):
    pg.display.set_mode(
        sizes[0],
        flags=pg.FULLSCREEN | pg.SRCALPHA | pg.SCALED,
        vsync=1,
    )

DISPLAYSURF = pg.Surface((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT), flags=pg.SRCALPHA)

ALL_CHANGES_DISPLAYSURF: list[pg.Rect] = []
