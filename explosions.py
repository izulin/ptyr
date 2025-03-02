from __future__ import annotations

import random

from pygame import Vector2, Vector3

from assets import (
    LargeExplosionAnimation1,
    LargeExplosionAnimation2,
    MediumExplosionAnimation,
)
from groups import try_and_spawn_object
from objects import AnimatedDrawable, Collides, HasMass, HasTimer, Object, UsesPhysics
from particles import CollidingParticle


def explosion_effect(
    owner: Object,
    init_speed: float = 0.1,
    particles: int | None = None,
    pos_spread: float | None = None,
):
    if pos_spread is None:
        pos_spread = owner.get_surface().get_rect().h / 2
    if particles is None:
        particles = int(owner.mass)

    def _tmp():
        dpos = Vector3(
            *Vector2(random.uniform(pos_spread, pos_spread * 1.5), 0.0).rotate(
                random.uniform(0, 360),
            ),
            0.0,
        )
        dspeed = Vector3(*Vector2(init_speed, 0.0).rotate(random.uniform(0, 360)), 0.0)
        return CollidingParticle(
            init_pos=owner.pos + dpos,
            init_speed=owner.speed + dspeed,
            ttl=random.uniform(500, 1000),
        )

    try_and_spawn_object(_tmp, particles, 2 * particles)


class Explosion(AnimatedDrawable, HasTimer, Collides, UsesPhysics, HasMass, Object):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, owner=owner, mass=owner.mass, **kwargs)
        assert self.ttl == self._image.animation_time


class LargeExplosion(Explosion):
    TTL = LargeExplosionAnimation1.animation_time
    IMAGE = (LargeExplosionAnimation1, LargeExplosionAnimation2)


class HugeExplosion(Explosion):
    TTL = LargeExplosionAnimation1.animation_time
    IMAGE = (
        LargeExplosionAnimation1.scale_by(2),
        LargeExplosionAnimation2.scale_by(2),
    )


class MediumExplosion(Explosion):
    TTL = MediumExplosionAnimation.animation_time
    IMAGE = MediumExplosionAnimation


class SmallExplosion(Explosion):
    TTL = MediumExplosionAnimation.animation_time / 2
    IMAGE = MediumExplosionAnimation.scale_by(0.5, 0.5)
