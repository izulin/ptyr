from __future__ import annotations
import pygame as pg
from pygame import Vector3

from consts import YELLOW, RED
from objects import MovingObject, DrawableObject, HasTimer, NoControl
from surface import CachedSurface


class Particle(NoControl, HasTimer, DrawableObject, MovingObject):
    IMAGE = None
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def get_surface(self) -> CachedSurface:
        r = 1
        tmp = pg.surface.Surface((2 * r + 1, 2 * r + 1), flags=pg.SRCALPHA)
        t = min(1, self.alive_time / self.ttl)
        print(t)
        pg.draw.circle(tmp, pg.Color.lerp(YELLOW, RED, t), (r, r), r)
        return CachedSurface(tmp, no_rotation=True)
