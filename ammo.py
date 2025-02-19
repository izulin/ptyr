from assets import SmallBulletImage, MineAnimation
from explosions import HugeExplosion
from objects import (
    Collides,
    NoControl,
    MovingObject,
    HasTimer,
    StaticDrawable,
    AnimatedDrawable,
    HasHitpoints,
)


class Bullet(Collides, NoControl, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, owner, **kwargs):
        self.owner = owner
        super().__init__(*args, **kwargs)

    def on_collision(self, other: MovingObject):
        if other != self.owner:
            other.apply_damage(self.DMG)
            self.mark_dead()
        super().on_collision(other)

    def apply_damage(self, dmg):
        self.mark_dead()


class SmallBullet(StaticDrawable, HasTimer, Bullet):
    MASS = 1.0 / 10
    TTL = 3_000
    DMG = 10.0
    IMAGE = SmallBulletImage


class Mine(AnimatedDrawable, Collides, HasHitpoints, NoControl, MovingObject):
    DMG = 1000.0
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    IMAGE = MineAnimation
    HP = 5.0
    MASS = 10.0

    def __init__(self, *args, owner, **kwargs):
        self.owner = owner
        super().__init__(*args, **kwargs)

    def on_collision(self, other: MovingObject):
        if isinstance(other, HasHitpoints) and other.HP >= 30 and other != self.owner:
            other.apply_damage(self.DMG)
            self.mark_dead()

    def on_death(self):
        HugeExplosion(init_pos=self.pos, init_speed=self.speed)
        super().on_death()
