from __future__ import annotations

import pygame as pg
from pygame.math import Vector2

from config import CONFIG

BLUE = pg.Color(0, 0, 255)
RED = pg.Color(255, 0, 0)
GREEN = pg.Color(0, 255, 0)
CYAN = pg.Color(0, 255, 255)
YELLOW = pg.Color(255, 255, 0)
PURPLE = pg.Color(255, 0, 255)
BLACK = pg.Color(0, 0, 0)
WHITE = pg.Color(255, 255, 255)

ALL_SHIFTS = [
    Vector2(-CONFIG.WORLD_WIDTH, -CONFIG.WORLD_HEIGHT),
    Vector2(-CONFIG.WORLD_WIDTH, 0),
    Vector2(-CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT),
    Vector2(0, -CONFIG.WORLD_HEIGHT),
    Vector2(0, 0),
    Vector2(0, CONFIG.WORLD_HEIGHT),
    Vector2(CONFIG.WORLD_WIDTH, -CONFIG.WORLD_HEIGHT),
    Vector2(CONFIG.WORLD_WIDTH, 0),
    Vector2(CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT),
]
