from __future__ import annotations

from pygame import Vector3, Vector2

from assets import (
    LargeExplosionAnimation1,
    LargeExplosionAnimation2,
    MediumExplosionAnimation,
)
from groups import ALL_COLLIDING_OBJECTS
from objects import AnimatedDrawable, NoControl, HasTimer, MovingObject, Collides
from particles import ExplosionParticle
import random
import math


class Explosion(AnimatedDrawable, HasTimer, NoControl, Collides, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, owner=owner, mass=owner.mass, **kwargs)
        assert self.ttl == self._image.animation_time
        POS_SPREAD = math.sqrt(owner.inertia_moment / owner.mass)
        SPEED_SPREAD = 0.05
        cnt = 0
        while cnt < int(owner.mass):
            ep = ExplosionParticle(
                init_pos=self.pos
                + Vector3(
                    *Vector2(POS_SPREAD * 2, 0.0).rotate(random.uniform(0, 360)), 0.0
                )
                + Vector3(
                    random.normalvariate(sigma=POS_SPREAD / 4),
                    random.normalvariate(sigma=POS_SPREAD / 4),
                    0,
                ),
                init_speed=self.speed
                + Vector3(
                    random.normalvariate(sigma=SPEED_SPREAD),
                    random.normalvariate(sigma=SPEED_SPREAD),
                    0,
                ),
                ttl=random.uniform(250, 500),
            )
            if ALL_COLLIDING_OBJECTS.cd.collide_with_callback(ep, on_collision=None):
                ep.kill()
            else:
                cnt += 1


class LargeExplosion(Explosion):
    TTL = 1000
    IMAGE = (LargeExplosionAnimation1, LargeExplosionAnimation2)


class HugeExplosion(Explosion):
    TTL = 1000
    IMAGE = (
        LargeExplosionAnimation1.scale_by(2, 1),
        LargeExplosionAnimation2.scale_by(2, 1),
    )


class MediumExplosion(Explosion):
    TTL = 1000
    IMAGE = MediumExplosionAnimation


class SmallExplosion(Explosion):
    TTL = 500
    IMAGE = MediumExplosionAnimation.scale_by(0.5, 0.5)
