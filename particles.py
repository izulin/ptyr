from __future__ import annotations
import pygame as pg

from consts import YELLOW, RED
from groups import ALL_PARTICLES
from objects import MovingObject, DrawableObject, HasTimer, NoControl, Collides
from surface import CachedSurface

particles_cache: dict[tuple[int, ...], CachedSurface] = {}


class Particle(NoControl, HasTimer, DrawableObject, MovingObject):
    IMAGE = None
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, **kwargs):
        self._layer = -1
        super().__init__(ALL_PARTICLES, *args, **kwargs)

    def get_surface(self) -> CachedSurface:
        t = min(1, self.alive_time / self.ttl)
        color = pg.Color.lerp(YELLOW, RED, t)

        if tuple(color) not in particles_cache:
            tmp = pg.surface.Surface((2, 2), flags=pg.SRCALPHA)
            tmp.fill(color)
            particles_cache[tuple(color)] = CachedSurface(tmp, no_rotation=True)
        return particles_cache[tuple(color)]


class ExplosionParticle(Collides, Particle):
    MASS = 0.5

    def on_collision(self, other: MovingObject):
        other.apply_damage(0.1)
        self.mark_dead()
