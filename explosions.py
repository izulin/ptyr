from pygame import Vector2

from assets import (
    LargeExplosionAnimation1,
    LargeExplosionAnimation2,
    MediumExplosionAnimation,
)
from groups import ALL_EXPLOSIONS
from objects import AnimatedDrawable, NoControl, HasTimer, MovingObject


class Explosion(AnimatedDrawable, HasTimer, NoControl, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(ALL_EXPLOSIONS, *args, **kwargs)
        assert self.ttl == self._image.animation_time
        self._dt = 0

    def update(self, dt: float):
        self._dt = dt
        super().update(dt)

    def on_collision(self, obj: MovingObject):
        distance = Vector2.distance_to(self.pos_xy, obj.pos_xy)
        obj.apply_damage(self._dt / self.TTL * self.DMG / max(1, distance))


class LargeExplosion(Explosion):
    TTL = 1000
    DMG = 100
    IMAGE = (LargeExplosionAnimation1, LargeExplosionAnimation2)


class HugeExplosion(Explosion):
    TTL = 1000
    DMG = 200
    IMAGE = (
        LargeExplosionAnimation1.scale_by(2, 1),
        LargeExplosionAnimation2.scale_by(2, 1),
    )


class SmallExplosion(Explosion):
    TTL = 500
    DMG = 50
    IMAGE = MediumExplosionAnimation.scale_by(0.5, 0.5)
