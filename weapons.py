from __future__ import annotations

import contextlib
import math

from pygame import Vector2, Vector3

from ammo import Mine, SmallBullet, SmallMissile
from assets import (
    DoubleShotWeaponImage,
    LaserShardImage,
    LaserWeaponImage,
    MineLauncherWeaponImage,
    MissileLauncherWeaponImage,
    SingleShotWeaponImage,
)
from groups import ALL_COLLIDING_OBJECTS, try_and_spawn_object
from math_utils import internal_coord_to_xy
from objects import Attached, Object, StaticDrawable
from status import Status
from teams import check_teams


class Weapon(Status):
    COOLDOWN: int | None = None
    AMMO: int | None = None

    cooldown: float
    ammo: int | None
    init_speed: float
    cooldown_left: float

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.priority = -1

        self.cooldown_left = 0.0
        assert self.COOLDOWN is not None
        self.cooldown = self.COOLDOWN
        self.ammo = self.AMMO

    def _fire_at_pos(self, launch_pos_internal, launch_angle, launch_speed):
        launch_speed_internal = Vector2(0.0, launch_speed).rotate(launch_angle)

        init_pos = self.owner.pos + Vector3(
            *internal_coord_to_xy(launch_pos_internal, self.owner.pos.z),
            launch_angle,
        )

        rotational_delta = launch_pos_internal.rotate(90) * math.radians(
            self.owner.speed.z,
        )

        init_speed = self.owner.speed + Vector3(
            *internal_coord_to_xy(
                launch_speed_internal + rotational_delta,
                self.owner.pos.z,
            ),
            0.0,
        )

        return try_and_spawn_object(
            lambda: self.AMMO_CLS(
                init_pos=init_pos,
                init_speed=init_speed,
                owner=self.owner,
            ),
            1,
            1,
        )

    def _recoil(self, launch_pos_internal, launch_angle, launch_speed):
        launch_speed_internal = Vector2(0.0, launch_speed).rotate(launch_angle)

        # momentum moment / inertia moment = angular speed
        rotational_recoil = (
            Vector3(launch_pos_internal.x, launch_pos_internal.y, 0.0).cross(
                Vector3(launch_speed_internal.x, launch_speed_internal.y, 0.0),
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
        super().__init__(*args, owner=owner, **kwargs)
        if owner.weapon.sprite != self:
            with contextlib.suppress(AttributeError):
                owner.weapon.sprite.kill()
        self.add(owner.weapon)


class Secondary:
    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, owner=owner, **kwargs)
        if owner.secondary_weapon.sprite != self:
            with contextlib.suppress(AttributeError):
                owner.secondary_weapon.sprite.kill()
        self.add(owner.secondary_weapon)


class LaserShard(StaticDrawable, Attached, Object):
    IMAGE = LaserShardImage.scale_by(0.75)

    def update(self, dt: float):
        for obj in ALL_COLLIDING_OBJECTS.cd.collide_with_callback(
            self,
            on_collision=None,
        ):
            if check_teams(self, obj):
                with contextlib.suppress(AttributeError):
                    obj.apply_damage(dt / 10)
        self.kill()


class LaserWeapon(Primary, Weapon):
    COOLDOWN = 0
    AMMO_CLS = LaserShard
    AMMO = None
    icon = LaserWeaponImage.scale((10, 10))

    def fire(self):
        for i in range(10):
            shard = self.AMMO_CLS(
                init_rel_pos=Vector3(
                    6,
                    13 + (self.AMMO_CLS.IMAGE.get_rect().h - 1) * (i + 1 / 2),
                    0,
                ),
                owner=self.owner,
                base_object=self.owner,
            )
            if col := ALL_COLLIDING_OBJECTS.cd.collide_with_callback(
                shard,
                on_collision=None,
            ):
                col = [c for c in col if c is not self.owner]
                if col:
                    break

        for i in range(10):
            shard = self.AMMO_CLS(
                init_rel_pos=Vector3(
                    -6,
                    13 + (self.AMMO_CLS.IMAGE.get_rect().h - 1) * (i + 1 / 2),
                    0,
                ),
                owner=self.owner,
                base_object=self.owner,
            )
            if col := ALL_COLLIDING_OBJECTS.cd.collide_with_callback(
                shard,
                on_collision=None,
            ):
                col = [c for c in col if c is not self.owner]
                if col:
                    break


class SingleShotWeapon(Primary, Weapon):
    AMMO_CLS = SmallBullet
    COOLDOWN = 100
    AMMO = None
    icon = SingleShotWeaponImage.scale((10, 10))

    def fire_logic(self):
        recoil = Vector3(0, 0, 0)
        if self._fire_at_pos(Vector2(0.0, 20.0), 0.0, 0.3):
            recoil += self._recoil(Vector2(0.0, 20.0), 0.0, 0.3)
        self.owner.speed -= recoil


class DoubleShotWeapon(Primary, Weapon):
    AMMO_CLS = SmallBullet
    COOLDOWN = 100
    AMMO = None
    icon = DoubleShotWeaponImage.scale((10, 10))

    def fire_logic(self):
        recoil = Vector3(0, 0, 0)
        if self._fire_at_pos(Vector2(5.0, 20.0), 0.0, 0.3):
            recoil += self._recoil(Vector2(5.0, 20.0), 0.0, 0.3)
        if self._fire_at_pos(Vector2(-5.0, 20.0), 0.0, 0.3):
            recoil += self._recoil(Vector2(-5.0, 20.0), 0.0, 0.3)
        self.owner.speed -= recoil


class SmallMissileWeapon(Secondary, Weapon):
    AMMO_CLS = SmallMissile
    COOLDOWN = 200
    AMMO = 50
    icon = MissileLauncherWeaponImage.scale((10, 10))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.side = True

    def fire_logic(self):
        if self._fire_at_pos(Vector2(20.0 if self.side else -20.0, 10.0), 0.0, 0.1):
            self.ammo -= 1
        self.side = not self.side


class MineLauncher(Secondary, Weapon):
    AMMO_CLS = Mine
    COOLDOWN = 1000
    AMMO = 10
    icon = MineLauncherWeaponImage.scale((10, 10))

    def fire_logic(self):
        recoil = Vector3(0, 0, 0)
        if self._fire_at_pos(Vector2(0.0, -20.0), 180, 0.02):
            recoil += self._recoil(Vector2(0.0, -20.0), 180, 0.02)
            self.ammo -= 1
        self.owner.speed -= recoil
