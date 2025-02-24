from __future__ import annotations

from pygame import Vector3

from assets import SmallBulletImage, MineAnimation, SmallMissileImage
from engines import Engine
from explosions import explosion_effect, LargeExplosion, SmallExplosion
from objects import (
    Collides,
    MovingObject,
    HasTimer,
    StaticDrawable,
    AnimatedDrawable,
    HasHitpoints, HasEngines,
)


class Bullet(Collides, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0
    DMG: float

    def on_collision(self, other: MovingObject):
        if other != self.owner:
            other.apply_damage(self.DMG)
            self.mark_dead()
        super().on_collision(other)

    def apply_damage(self, dmg):
        self.mark_dead()


class SmallBullet(StaticDrawable, HasTimer, Bullet):
    MASS = 0.1
    TTL = 3_000
    DMG = 10.0
    IMAGE = SmallBulletImage

class SmallMissile(StaticDrawable, Collides, HasEngines, MovingObject):
    MASS = 2.0
    DMG = 30.0
    DRAG = 0.0
    ANGULAR_DRAG = 0.0
    IMAGE = SmallMissileImage
    acc_time = 2000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.back_engine = Engine(self, Vector3(0, -5, 180), 0.5)
        self.back_left_engine = Engine(self, Vector3(0,-5, 135), 0.05)
        self.back_right_engine = Engine(self, Vector3(0,-5,225), 0.05)

    def update(self, dt: float):
        self.back_engine.active = int(self.alive_time < self.acc_time)
        self.back_left_engine.active = int(self.speed.z <= 0) * int(self.alive_time < self.acc_time)
        self.back_right_engine.active = int(self.speed.z >= 0) * int(self.alive_time < self.acc_time)
        super().update(dt)


    def on_collision(self, other: MovingObject):
        if other != self.owner:
            other.apply_damage(self.DMG)
            self.mark_dead()
        super().on_collision(other)

    def apply_damage(self, dmg):
        self.mark_dead()

    def on_death(self):
        SmallExplosion(init_pos=self.pos, init_speed=self.speed, owner=self.owner)
        explosion_effect(self, particles=20)
        super().on_death()


class Mine(AnimatedDrawable, Collides, HasHitpoints, MovingObject):
    DMG = 1000.0
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    IMAGE = MineAnimation
    HP = 5.0
    MASS = 10.0

    def on_collision(self, other: MovingObject):
        if isinstance(other, HasHitpoints) and other.HP >= 30 and other != self.owner:
            other.apply_damage(self.DMG)
            self.mark_dead()

    def on_death(self):
        LargeExplosion(init_pos=self.pos, init_speed=self.speed, owner=self.owner)
        explosion_effect(self, particles=100)
        super().on_death()
