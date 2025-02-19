from __future__ import annotations
from pygame import Vector3, Vector2

from ammo import SmallBullet, Mine
from assets import (
    SingleShotWeaponImage,
    DoubleShotWeaponImage,
    MineLauncherWeaponImage,
)
from math_utils import internal_coord_to_xy
from status import Status
import math


class Weapon(Status):
    COOLDOWN = None
    AMMO = None

    cooldown: float
    ammo: int | None
    init_speed: float
    cooldown_left: float

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldown_left = 0.0
        assert self.COOLDOWN is not None
        self.cooldown = self.COOLDOWN
        self.ammo = self.AMMO

    def _fire_at_pos(self, launch_pos_internal, launch_angle, launch_speed):
        launch_speed_internal = Vector2(0.0, launch_speed).rotate(launch_angle)

        init_pos = self.owner.pos + Vector3(
            *internal_coord_to_xy(launch_pos_internal, self.owner.pos.z), launch_angle
        )

        rotational_delta = launch_pos_internal.rotate(90) * math.radians(
            self.owner.speed.z
        )

        init_speed = self.owner.speed + Vector3(
            *internal_coord_to_xy(
                launch_speed_internal + rotational_delta, self.owner.pos.z
            ),
            0.0,
        )
        self.AMMO_CLS(init_pos=init_pos, init_speed=init_speed, owner=self.owner)

    def _recoil(self, launch_pos_internal, launch_angle, launch_speed):
        launch_speed_internal = Vector2(0.0, launch_speed).rotate(launch_angle)

        # momentum moment / inertia moment = angular speed
        rotational_recoil = (
            Vector3(launch_pos_internal.x, launch_pos_internal.y, 0.0).cross(
                Vector3(launch_speed_internal.x, launch_speed_internal.y, 0.0)
            )
            * self.AMMO_CLS.MASS
            / self.owner.inertia_moment
            * math.degrees(1)
        )
        # moment / mass = speed
        recoil_xy = (
            internal_coord_to_xy(launch_speed_internal, self.owner.pos.z)
            * self.AMMO_CLS.MASS
            / self.owner.mass
        )

        return Vector3(recoil_xy.x, recoil_xy.y, 0) + rotational_recoil

    def update(self, dt):
        self.cooldown_left -= dt
        super().update(dt)

    def fire(self):
        if self.cooldown_left > 0:
            return
        if self.ammo is not None and self.ammo <= 0:
            return

        self.fire_logic()

        self.cooldown_left = self.cooldown
        if self.ammo is not None and self.ammo <= 0:
            self.kill()

    def fire_logic(self):
        raise NotImplementedError


class Primary:
    def __init__(self, *args, owner, **kwargs):
        if owner.weapon is not None and owner.weapon != self:
            owner.weapon.kill()
        owner.weapon = self
        super().__init__(*args, owner=owner, **kwargs)


class Secondary:
    def __init__(self, *args, owner, **kwargs):
        if owner.secondary_weapon is not None and owner.secondary_weapon != self:
            owner.secondary_weapon.kill()
        owner.secondary_weapon = self
        super().__init__(*args, owner=owner, **kwargs)


class SingleShotWeapon(Primary, Weapon):
    AMMO_CLS = SmallBullet
    COOLDOWN = 100
    AMMO = None
    icon = SingleShotWeaponImage.scale((10, 10))

    def fire_logic(self):
        self._fire_at_pos(Vector2(0.0, 20.0), 0.0, 0.3)
        self.owner.speed -= self._recoil(Vector2(0.0, 20.0), 0.0, 0.3)


class DoubleShotWeapon(Primary, Weapon):
    AMMO_CLS = SmallBullet
    COOLDOWN = 100
    AMMO = None
    icon = DoubleShotWeaponImage.scale((10, 10))

    def fire_logic(self):
        self._fire_at_pos(Vector2(5.0, 20.0), 0.0, 0.3)
        self._fire_at_pos(Vector2(-5.0, 20.0), 0.0, 0.3)
        self.owner.speed -= self._recoil(Vector2(5.0, 20.0), 0.0, 0.3) + self._recoil(
            Vector2(-5.0, 20.0), 0.0, 0.3
        )


class MineLauncher(Secondary, Weapon):
    AMMO_CLS = Mine
    COOLDOWN = 1000 / 10
    AMMO = 10
    icon = MineLauncherWeaponImage.scale((10, 10))

    def fire_logic(self):
        self._fire_at_pos(Vector2(0.0, -10.0), 180, 0.01)
        self.owner.speed -= self._recoil(Vector2(0.0, -10.0), 180, 0.01)
