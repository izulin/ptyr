from __future__ import annotations

from pygame import Vector3, Vector2

from assets import (
    LargeExplosionAnimation1,
    LargeExplosionAnimation2,
    MediumExplosionAnimation,
)
from groups import ALL_COLLIDING_OBJECTS
from objects import AnimatedDrawable, NoControl, HasTimer, MovingObject, Collides
from particles import CollidingParticle
import random


class Explosion(AnimatedDrawable, HasTimer, NoControl, Collides, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, owner=owner, mass=owner.mass, **kwargs)
        assert self.ttl == self._image.animation_time
        POS_SPREAD = owner.get_surface().get_rect().h / 2
        SPEED_SPREAD = 0.1
        ok = 0
        for cnt in range(int(owner.mass)):
            dpos = Vector3(
                *Vector2(random.uniform(POS_SPREAD, POS_SPREAD * 1.5), 0.0).rotate(
                    random.uniform(0, 360)
                ),
                0.0,
            )
            dspeed = Vector3(
                *Vector2(SPEED_SPREAD, 0.0).rotate(random.uniform(0, 360)), 0.0
            )
            ep = CollidingParticle(
                init_pos=self.pos + dpos,
                init_speed=self.speed + dspeed,
                ttl=random.uniform(500, 1000),
                mass=0.1,
            )
            if ALL_COLLIDING_OBJECTS.cd.collide_with_callback(ep, on_collision=None):
                ep.kill()
            else:
                ok += 1
        print(ok, owner.mass)


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
