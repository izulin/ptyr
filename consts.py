from __future__ import annotations
from pygame.math import Vector2

FPS = 1000
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

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
