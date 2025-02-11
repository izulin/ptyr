from __future__ import annotations
import pygame as pg

from groups import ALL_SPRITES
from math_utils import (
    normalize_pos3,
    range_kutta_2,
    internal_coord_to_xy,
)
from consts import WHITE, GREEN, RED, ALL_SHIFTS, SCREEN_HEIGHT, SCREEN_WIDTH, BLUE
from pygame.math import Vector3, Vector2
from collisions import ALL_SPRITES_CD
from surface import CachedSurface
import random


class MovingObject(pg.sprite.Sprite):
    DRAG = 1 / 1000
    ANGULAR_DRAG = 2 / 1000
    TTL = None
    HP = None
    SHIELD = None
    IMAGE = None
    GROUPS = (ALL_SPRITES,)
    COLLIDES = True

    _image: CachedSurface
    rect: pg.Rect
    pos: Vector3
    speed: Vector3
    mass: float
    ttl: float | None
    alive_time: float
    hp: float | None
    shield: float | None
    alive: bool

    def __init__(self, *args, image=None, init_pos, init_speed, **kwargs):
        super().__init__(*self.GROUPS, *args, **kwargs)

        if image is None:
            image = self.IMAGE

        if isinstance(image, (list, tuple)):
            self._image = random.choice(image)
        else:
            self._image = image

        self.pos = normalize_pos3(Vector3(init_pos))
        self.speed = Vector3(init_speed)
        self.alive_time = 0.0

        self.update_image_rect()
        self._acc = Vector2()
        self._drag = Vector2()
        self.mass = self.MASS
        self.ttl = self.TTL
        self.hp = self.HP
        self.shield = self.SHIELD
        ALL_SPRITES_CD.add(self)
        self.alive = self.get_alive()

    def make_dead(self):
        self.alive = False
        self.on_death()

    def kill(self):
        ALL_SPRITES_CD.remove(self)
        super().kill()

    def apply_damage(self, dmg: float):
        if self.shield is not None:
            d = min(self.shield, dmg)
            self.shield -= d
            dmg -= d
        if self.hp is not None:
            self.hp -= dmg

    def heal_hp(self, heal: float):
        if self.hp is not None:
            self.hp = min(self.hp + heal, self.HP)

    def heal_shield(self, heal: float):
        if self.shield is not None:
            self.shield = min(self.shield + heal, self.SHIELD)

    def on_collision(self, other: MovingObject):
        pass

    def draw_ui(self, target: pg.Surface) -> list[pg.Rect]:
        assert (
            target.get_width() == SCREEN_WIDTH and target.get_height() == SCREEN_HEIGHT
        )
        all_changes = []
        for shift in ALL_SHIFTS:
            rect: pg.Rect = self.get_surface().get_rect(center=self.rect.center + shift)
            hp_bar = pg.Rect(0, 0, 40, 5)
            hp_bar.midbottom = rect.midtop
            shield_bar = pg.Rect(0, 0, 40, 5)
            shield_bar.midbottom = hp_bar.midtop
            if self.hp is not None:
                all_changes.append(pg.draw.rect(target, GREEN, hp_bar, width=1))
                hp_bar.width = hp_bar.width * (self.hp / self.HP)
                all_changes.append(pg.draw.rect(target, GREEN, hp_bar))
            if self.shield is not None:
                all_changes.append(pg.draw.rect(target, BLUE, shield_bar, width=1))
                shield_bar.width = shield_bar.width * (self.shield / self.SHIELD)
                all_changes.append(pg.draw.rect(target, BLUE, shield_bar))
        return all_changes

    def get_alive(self) -> bool:
        return (self.ttl is None or self.ttl > self.alive_time) and (
            self.hp is None or self.hp > 0
        )

    @property
    def pos_xy(self) -> Vector2:
        return Vector2(self.pos.x, self.pos.y)

    @property
    def speed_xy(self) -> Vector2:
        return Vector2(self.speed.x, self.speed.y)

    def draw_debugs(self, target: pg.Surface) -> list[pg.Rect]:
        assert (
            target.get_width() == SCREEN_WIDTH and target.get_height() == SCREEN_HEIGHT
        )
        pos_xy = self.pos_xy
        speed_xy = self.speed_xy
        all_changes = []
        for shift in ALL_SHIFTS:
            dt = 200
            all_changes.append(
                pg.draw.line(
                    target,
                    WHITE,
                    shift + pos_xy,
                    shift + pos_xy + dt * speed_xy,
                    1,
                )
            )
            dt = 200000
            all_changes.append(
                pg.draw.line(
                    target,
                    GREEN,
                    shift + pos_xy,
                    shift + pos_xy + dt * self._acc,
                    1,
                )
            )
            all_changes.append(
                pg.draw.line(
                    target,
                    RED,
                    shift + pos_xy + dt * self._acc,
                    shift + pos_xy + dt * self._acc - dt * self._drag,
                    1,
                )
            )
        return all_changes

    def get_surface(self) -> CachedSurface:
        return self._image

    def update_image_rect(self):
        self.image = self.get_surface().get_image(self.pos.z)
        self.rect = self.get_surface().get_rect(self.pos.z, center=self.pos_xy)
        self.mask = self.get_surface().get_mask(self.pos.z)

    def update(self, dt: float):
        if not self.alive:
            self.kill()
            return
        old_rect = self.rect
        self.update_pos(dt)
        self.update_image_rect()
        ALL_SPRITES_CD.move(self, self.rect, old_rect)
        self.alive_time += dt
        self.heal_shield(dt / 1000)
        if not self.get_alive():
            self.make_dead()
            self.kill()

    def on_death(self):
        pass

    def get_accels(self):
        raise NotImplementedError

    def update_pos(self, dt: float):
        accel, angular_accel = self.get_accels()

        def f(pos: Vector3, speed: Vector3):
            self._acc = internal_coord_to_xy(accel, pos.z)
            angular_drag = speed.z * abs(speed.z) * self.ANGULAR_DRAG

            speed_xy = Vector2(speed.x, speed.y)
            # |drag| = self.DRAG * |speed|**2
            self._drag = speed_xy.length() * self.DRAG * speed_xy

            acc = Vector3(*(self._acc - self._drag), angular_accel - angular_drag)

            return speed, acc

        new_pos, new_speed = range_kutta_2(f, self.pos, self.speed, dt)

        self.pos = normalize_pos3(new_pos)
        self.speed = new_speed


class PassiveObject(MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def get_accels(self):
        return Vector2(0.0, 0.0), 0.0
