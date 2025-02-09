from __future__ import annotations

import pygame
from pygame import Vector3, Vector2

from assets import SmallPlasmaImage
from groups import ALL_BULLETS
from math_utils import internal_coord_to_xy
from typing import TYPE_CHECKING

from objects import PassiveObject, MovingObject

if TYPE_CHECKING:
    from players import Player


class Bullet(PassiveObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(ALL_BULLETS)

    def on_collision(self, other: MovingObject):
        other.apply_damage(self.DMG)
        self.hp = 0

    def draw_ui(self, target: pygame.Surface) -> list[pygame.Rect]:
        return []


class SmallPlasma(Bullet):
    MASS = 1.0 / 10
    TTL = 3_000
    HP = 1.0
    DMG = 5.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, image=SmallPlasmaImage)


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

        r = self.owner.images[0].get_height() / 2
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


class SinglePlasma(BasicWeapon):
    AMMO_CLS = SmallPlasma
    COOLDOWN = 50
    AMMO = None

    def fire_logic(self):
        pos = Vector2(0.0, 20.0)
        launch_angle = 0.0
        launch_speed = 0.3

        self._fire_at_pos(pos, launch_angle, launch_speed)
        self.owner.speed -= self._recoil(pos, launch_angle, launch_speed)
