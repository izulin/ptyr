from __future__ import annotations

import pygame as pg
from pygame import Vector3, Vector2

from assets import SmallBulletImage, MineAnimation
from math_utils import internal_coord_to_xy
from typing import TYPE_CHECKING

from objects import PassiveObject, MovingObject
from surface import CachedSurface

if TYPE_CHECKING:
    from players import Player


class BasicWeapon:
    COOLDOWN = None
    AMMO = None

    owner: Player
    cooldown: float
    ammo: int | None
    init_speed: float
    cooldown_left: float

    def __init__(self, *, owner):
        self.owner = owner

        self.cooldown_left = 0.0
        assert self.COOLDOWN is not None
        self.cooldown = self.COOLDOWN
        self.ammo = self.AMMO

    def update(self, dt):
        self.cooldown_left -= dt

    def _fire_at_pos(self, launch_pos_internal, launch_angle, launch_speed):
        launch_speed_internal = Vector2(0.0, launch_speed).rotate(launch_angle)

        init_pos = self.owner.pos + Vector3(
            *internal_coord_to_xy(launch_pos_internal, self.owner.pos.z), launch_angle
        )

        rotational_delta = (
            launch_pos_internal.rotate(90) * self.owner.speed.z * 3.14 / 180
        )

        init_speed = self.owner.speed + Vector3(
            *internal_coord_to_xy(
                launch_speed_internal + rotational_delta, self.owner.pos.z
            ),
            0.0,
        )
        self.AMMO_CLS(init_pos=init_pos, init_speed=init_speed)

    def _recoil(self, launch_pos_internal, launch_angle, launch_speed):
        launch_speed_internal = Vector2(0.0, launch_speed).rotate(launch_angle)

        r = self.owner.get_image().get_image().get_height() / 2
        m = self.AMMO_CLS.MASS
        rotational_recoil = (
            Vector3(*launch_pos_internal, 0.0)
            .cross(Vector3(*launch_speed_internal, 0.0))
            .z
            * m
            / (1 / 4 * self.owner.mass * r**2)
            * 180
            / 3.14
        )
        recoil_xy = (
            internal_coord_to_xy(launch_speed_internal, self.owner.pos.z)
            * m
            / self.owner.mass
        )

        return Vector3(*recoil_xy, rotational_recoil)

    def fire(self):
        if self.cooldown_left > 0:
            return
        if self.ammo is not None and self.ammo <= 0:
            return

        self.fire_logic()

        self.cooldown_left = self.cooldown
        if self.ammo is not None and self.ammo <= 0:
            self.owner.weapon = self.owner.default_weapon()

    def fire_logic(self):
        raise NotImplementedError


class Bullet(PassiveObject):
    def on_collision(self, other: MovingObject):
        other.apply_damage(self.DMG)
        self.hp = 0

    def draw_ui(self, target: pg.Surface) -> list[pg.Rect]:
        return []


class SmallParticle(Bullet):
    MASS = 1.0 / 10
    TTL = 3_000
    HP = 1.0
    DMG = 1.0
    IMAGE = SmallBulletImage


class SingleShot(BasicWeapon):
    AMMO_CLS = SmallParticle
    COOLDOWN = 50
    AMMO = None

    def fire_logic(self):
        self._fire_at_pos(Vector2(0.0, 20.0), 0.0, 0.3)
        self.owner.speed -= self._recoil(Vector2(0.0, 20.0), 0.0, 0.3)


class DoubleShot(BasicWeapon):
    AMMO_CLS = SmallParticle
    COOLDOWN = 100
    AMMO = None

    def fire_logic(self):
        self._fire_at_pos(Vector2(5.0, 20.0), 0.0, 0.3)
        self._fire_at_pos(Vector2(-5.0, 20.0), 0.0, 0.3)
        self.owner.speed -= self._recoil(Vector2(0.0, 20.0), 0.0, 0.3) + self._recoil(
            Vector2(0.0, 20.0), 0.0, 0.3
        )


class Mine(PassiveObject):
    DMG = 1000.0
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    IMAGE = MineAnimation
    HP = 100.0
    MASS = 100.0

    def on_collision(self, other: MovingObject):
        if other.HP is not None and other.HP >= 30:
            other.apply_damage(self.DMG)
            self.hp = 0

    def get_image(self) -> CachedSurface:
        return self.IMAGE.get_frame(
            (self.alive_time / (3000 / len(self.IMAGE))) % len(self.IMAGE)
        )

    def draw_ui(self, target: pg.Surface) -> list[pg.Rect]:
        return []


class MineLauncher(BasicWeapon):
    AMMO_CLS = Mine
    COOLDOWN = 1000
    AMMO = 10

    def fire_logic(self):
        self._fire_at_pos(Vector2(0.0, -10.0), 180, 0.01)
        self.owner.speed -= self._recoil(Vector2(0.0, -10.0), 180, 0.01)
