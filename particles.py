from __future__ import annotations
import pygame as pg

from consts import YELLOW, RED, BLACK, WHITE
from objects import Object, DrawableObject, HasTimer, Collides, UsesPhysics, HasMass
from surface import CachedSurface

particles_cache: dict[tuple[int, ...], CachedSurface] = {}


def mix(c1, c2, c3, c4, t):
    c34 = pg.Color.lerp(c3, c4, t / (3 - 2 * t))
    c12 = pg.Color.lerp(c1, c2, 3 * t / (1 + 2 * t))
    return pg.Color.lerp(c12, c34, t**2 * (3 - 2 * t))


class Particle(HasTimer, UsesPhysics, DrawableObject, Object):
    IMAGE = None
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, **kwargs):
        self._layer = -1
        super().__init__(*args, **kwargs)

    def get_surface(self) -> CachedSurface:
        t = min(1, self.alive_time / self.ttl)
        color = mix(WHITE, YELLOW, RED, BLACK, t)

        if tuple(color) not in particles_cache:
            tmp = pg.surface.Surface((2, 2), flags=pg.SRCALPHA)
            tmp.fill(color)
            particles_cache[tuple(color)] = CachedSurface(tmp, no_rotation=True)
        return particles_cache[tuple(color)]


class CollidingParticle(Collides, HasMass, Particle):
    MASS = 0.1

    def on_collision(self, other: Object):
        if not isinstance(other, CollidingParticle):
            try:
                other.apply_damage(0.1)
            except AttributeError:
                pass
            self.mark_dead()
