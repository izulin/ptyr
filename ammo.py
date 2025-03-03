from __future__ import annotations

import contextlib

from pygame import Vector3

from assets import MineAnimation, SmallBulletImage, SmallMissileImage
from consts import CYAN
from engines import Engine
from explosions import LargeExplosion, SmallExplosion, explosion_effect
from objects import (
    AnimatedDrawable,
    Collides,
    HasEngines,
    HasHitpoints,
    HasMass,
    HasTimer,
    Object,
    StaticDrawable,
    UsesPhysics,
)
from postprocessing import with_outline


class Bullet(UsesPhysics, HasMass, Collides, Object):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0
    DMG: float

    def on_collision(self, other: Object):
        if other != self.owner:
            with contextlib.suppress(AttributeError):
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


class SmallMissile(
    StaticDrawable,
    HasEngines,
    UsesPhysics,
    HasMass,
    HasTimer,
    Collides,
    Object,
):
    MASS = 2.0
    DMG = 30.0
    DRAG = 0.0
    ANGULAR_DRAG = 0.0
    IMAGE = SmallMissileImage
    acc_time = 1_000
    TTL = 3_000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.back_engine = Engine(self, Vector3(0, -5, 180), 0.5)
        self.back_left_engine = Engine(self, Vector3(0, -5, 135), 0.05)
        self.back_right_engine = Engine(self, Vector3(0, -5, 225), 0.05)

    def update(self, dt: float):
        self.back_engine.active = int(self.alive_time < self.acc_time)
        self.back_left_engine.active = int(self.speed.z <= 0) * int(
            self.alive_time < self.acc_time,
        )
        self.back_right_engine.active = int(self.speed.z >= 0) * int(
            self.alive_time < self.acc_time,
        )
        super().update(dt)

    def with_postprocessing(self):
        return with_outline(self, CYAN)

    def on_collision(self, other: Object):
        if other != self.owner:
            with contextlib.suppress(AttributeError):
                other.apply_damage(self.DMG)
            self.mark_dead()
        super().on_collision(other)

    def apply_damage(self, dmg):
        self.mark_dead()

    def on_death(self):
        SmallExplosion(init_pos=self.pos, init_speed=self.speed, owner=self.owner)
        explosion_effect(self, particles=20)
        super().on_death()


class Mine(AnimatedDrawable, Collides, UsesPhysics, HasHitpoints, HasMass, Object):
    DMG = 1000.0
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    IMAGE = MineAnimation
    HP = 5.0
    MASS = 10.0

    def on_collision(self, other: Object):
        if isinstance(other, HasHitpoints) and other.HP >= 30 and other != self.owner:
            other.apply_damage(self.DMG)
            self.mark_dead()

    def with_postprocessing(self):
        return with_outline(self, self.owner.color)

    def on_death(self):
        LargeExplosion(init_pos=self.pos, init_speed=self.speed, owner=self.owner)
        explosion_effect(self, particles=100)
        super().on_death()
