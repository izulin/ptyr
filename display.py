import pygame as pg

from config import CONFIG

DISPLAYSURF = pg.display.set_mode(
    (CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT),
    flags=pg.NOFRAME | pg.SRCALPHA | pg.SCALED,
)

ALL_CHANGES_DISPLAYSURF: list[pg.Rect] = []
