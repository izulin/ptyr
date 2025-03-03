from __future__ import annotations

import contextlib

import pygame as pg

from consts import BLACK, RED, WHITE, YELLOW
from objects import Collides, DrawableObject, HasMass, HasTimer, MovesSimplified, Object
from surface import CachedSurface

particles_cache: dict[tuple[int, ...], CachedSurface] = {}
color_mixer_cache: dict = {}


def mix(c1: pg.Color, c2: pg.Color, c3: pg.Color, c4: pg.Color, t: float) -> pg.Color:
    c34 = pg.Color.lerp(c3, c4, t / (3 - 2 * t))
    c12 = pg.Color.lerp(c1, c2, 3 * t / (1 + 2 * t))
    return pg.Color.lerp(c12, c34, t**2 * (3 - 2 * t))


class Particle(HasTimer, MovesSimplified, DrawableObject, Object):
    IMAGE = None

    def __init__(self, *args, **kwargs):
        self._layer = -1
        super().__init__(*args, **kwargs)

    def get_surface(self) -> CachedSurface:
        t = int(100 * min(1, self.alive_time / self.ttl))
        if t not in color_mixer_cache:
            color_mixer_cache[t] = mix(WHITE, YELLOW, RED, BLACK, t / 100)
        color = color_mixer_cache[t]

        if tuple(color) not in particles_cache:
            tmp = pg.surface.Surface((2, 2), flags=pg.SRCALPHA)
            tmp.fill(color)
            particles_cache[tuple(color)] = CachedSurface(tmp, no_rotation=True)
        return particles_cache[tuple(color)]


class CollidingParticle(Collides, HasMass, Particle):
    MASS = 0.1

    def on_collision(self, other: Object):
        if not isinstance(other, CollidingParticle):
            with contextlib.suppress(AttributeError):
                other.apply_damage(0.1)
            self.mark_dead()
