from __future__ import annotations
from pygame.math import Vector2
import pygame as pg

FPS = 1000
BLUE = pg.Color(0, 0, 255)
RED = pg.Color(255, 0, 0)
GREEN = pg.Color(0, 255, 0)
CYAN = pg.Color(0, 255, 255)
YELLOW = pg.Color(255, 255, 0)
BLACK = pg.Color(0, 0, 0)
WHITE = pg.Color(255, 255, 255)

SCREEN_WIDTH = 640 * 2
SCREEN_HEIGHT = 480 * 2

ALL_SHIFTS = [
    Vector2(-SCREEN_WIDTH, -SCREEN_HEIGHT),
    Vector2(-SCREEN_WIDTH, 0),
    Vector2(-SCREEN_WIDTH, SCREEN_HEIGHT),
    Vector2(0, -SCREEN_HEIGHT),
    Vector2(0, 0),
    Vector2(0, SCREEN_HEIGHT),
    Vector2(SCREEN_WIDTH, -SCREEN_HEIGHT),
    Vector2(SCREEN_WIDTH, 0),
    Vector2(SCREEN_WIDTH, SCREEN_HEIGHT),
]
