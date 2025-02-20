import pygame as pg

from consts import SCREEN_WIDTH, SCREEN_HEIGHT

DISPLAYSURF = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pg.NOFRAME | pg.SRCALPHA | pg.SCALED,
)

ALL_CHANGES_DISPLAYSURF: list[pg.Rect] = []
