from __future__ import annotations

import pygame as pg

from groups import (
    GroupWithCD,
    ALL_DRAWABLE_OBJECTS,
    ALL_COLLIDING_OBJECTS,
    ALL_UI_DRAWABLE_OBJECTS,
)
from math_utils import (
    normalize_pos3,
    range_kutta_2,
    internal_coord_to_xy,
)
from consts import (
    WHITE,
    GREEN,
    RED,
    ALL_SHIFTS,
    BLACK,
    YELLOW,
)
from pygame.math import Vector3, Vector2
import random
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from surface import CachedSurface, CachedAnimation

from surface import CachedSurface
from display import DISPLAYSURF, ALL_CHANGES_DISPLAYSURF

logger = logging.getLogger(__name__)


class MovingObject(pg.sprite.Sprite):
    pos: Vector3
    speed: Vector3
    alive_time: float
    alive_state: bool
    all_statuses: pg.sprite.Group
    all_engines: pg.sprite.Group
    _id: int
    DRAG: float
    ANGULAR_DRAG: float

    def __init__(self, *args, init_pos, init_speed, owner=None, **kwargs):
        assert not kwargs
        super().__init__()
        self.pos = normalize_pos3(Vector3(init_pos))
        self.speed = Vector3(init_speed)
        self.alive_time = 0.0

        self.alive_state = True
        self.update_image_rect()
        self._acc = Vector2()
        self._drag = Vector2()
        self.all_statuses = pg.sprite.Group()
        self.all_engines = pg.sprite.Group()
        self.add(ALL_DRAWABLE_OBJECTS, *args)
        if owner is None:
            owner = self
        self.owner = owner

    def kill(self):
        for status in self.all_statuses:
            status.kill()
        for engine in self.all_engines:
            engine.kill()
        super().kill()

    def mark_dead(self):
        self.alive_state = False

    def apply_damage(self, dmg: float):
        pass

    def heal_hp(self, heal: float):
        pass

    @property
    def pos_xy(self) -> Vector2:
        return Vector2(self.pos.x, self.pos.y)

    @property
    def speed_xy(self) -> Vector2:
        return Vector2(self.speed.x, self.speed.y)

    def draw_debugs(self):
        pos_xy = self.pos_xy
        speed_xy = self.speed_xy
        for shift in ALL_SHIFTS:
            dt = 200
            ALL_CHANGES_DISPLAYSURF.append(
                pg.draw.line(
                    DISPLAYSURF,
                    WHITE,
                    shift + pos_xy,
                    shift + pos_xy + dt * speed_xy,
                    1,
                )
            )
            dt = 200000
            ALL_CHANGES_DISPLAYSURF.append(
                pg.draw.line(
                    DISPLAYSURF,
                    GREEN,
                    shift + pos_xy,
                    shift + pos_xy + dt * self._acc,
                    1,
                )
            )
            ALL_CHANGES_DISPLAYSURF.append(
                pg.draw.line(
                    DISPLAYSURF,
                    RED,
                    shift + pos_xy + dt * self._acc,
                    shift + pos_xy + dt * self._acc - dt * self._drag,
                    1,
                )
            )

    def update(self, dt: float):
        new_pos, new_speed = self.updated_pos(dt)
        self.pos = normalize_pos3(new_pos)
        self.speed = new_speed
        self.alive_time += dt

    def on_death(self):
        pass

    def get_accels(self):
        raise NotImplementedError

    def updated_pos(self, dt: float):
        all_accel = self.get_accels()

        def f(pos: Vector3, speed: Vector3):
            self._acc = internal_coord_to_xy(Vector2(all_accel.x, all_accel.y), pos.z)
            angular_drag = speed.z * abs(speed.z) * self.ANGULAR_DRAG
            speed_xy = Vector2(speed.x, speed.y)
            # |drag| = self.DRAG * |speed|**2
            self._drag = speed_xy.length() * self.DRAG * speed_xy
            acc = self._acc - self._drag
            return speed, Vector3(acc.x, acc.y, all_accel.z - angular_drag)

        return range_kutta_2(f, self.pos, self.speed, dt)


class DrawableObject(MovingObject):
    image: pg.Surface
    rect: pg.Rect
    mask: pg.Mask

    def __init__(self, *args, image=None, **kwargs):
        if image is None:
            image = self.IMAGE

        if isinstance(image, (list, tuple)):
            self._image = random.choice(image)
        else:
            self._image = image
        super().__init__(ALL_DRAWABLE_OBJECTS, *args, **kwargs)

    def get_surface(self) -> CachedSurface:
        raise NotImplementedError

    def update_image_rect(self):
        self.image = self.get_surface().get_image(self.pos.z)
        self.rect = self.get_surface().get_rect(
            self.pos.z,
            topleft=self.pos_xy - self.get_surface().get_centroid(self.pos.z),
        )
        self.mask = self.get_surface().get_mask(self.pos.z)

    def update(self, dt: float):
        old_rect = self.rect
        super().update(dt)
        self.update_image_rect()
        for group in self.groups():
            if isinstance(group, GroupWithCD):
                group.cd.move(self, self.rect, old_rect)


class StaticDrawable(DrawableObject):
    _image: CachedSurface

    def get_surface(self) -> CachedSurface:
        return self._image


class AnimatedDrawable(DrawableObject):
    _image: CachedAnimation

    def get_surface(self) -> CachedSurface:
        return self._image.get_frame(self.alive_time)


class DrawsUI(DrawableObject):
    def __init__(self, *args, **kwargs):
        super().__init__(ALL_UI_DRAWABLE_OBJECTS, *args, **kwargs)

    def draw_ui(self) -> None:
        for shift in ALL_SHIFTS:
            rect: pg.Rect = self.get_surface().get_rect(center=self.rect.center + shift)

            def draw_bar(color, fill, _rect) -> pg.Rect:
                bar = pg.Rect(0, 0, 40, 3)
                bar.midbottom = _rect.midtop
                _rect = bar.copy()
                ALL_CHANGES_DISPLAYSURF.append(pg.draw.rect(DISPLAYSURF, BLACK, bar))
                ALL_CHANGES_DISPLAYSURF.append(
                    pg.draw.rect(DISPLAYSURF, color, bar, width=1)
                )
                bar.width = bar.width * fill
                ALL_CHANGES_DISPLAYSURF.append(pg.draw.rect(DISPLAYSURF, color, bar))
                return _rect

            if isinstance(self, HasHitpoints):
                rect = draw_bar(RED, self.hp / self.HP, rect)
            if isinstance(self, HasShield):
                rect = draw_bar(YELLOW, self.shield / self.SHIELD, rect)

            first = True
            for status in self.all_statuses:
                icon: pg.Surface = status.icon
                if first:
                    rect = icon.get_rect(bottomleft=rect.topleft)
                else:
                    rect = icon.get_rect(bottomleft=rect.bottomright)
                ALL_CHANGES_DISPLAYSURF.append(DISPLAYSURF.blit(icon, rect))
                first = False


class Collides(DrawableObject):
    mass: float

    def __init__(self, *args, mass=None, **kwargs):
        super().__init__(ALL_COLLIDING_OBJECTS, *args, **kwargs)
        if mass is None:
            mass = self.MASS
        self.mass = mass

    def on_collision(self, other: MovingObject):
        pass

    @property
    def inertia_moment(self):
        return self.get_surface().inertia_moment_coef * self.mass


class HasShield(MovingObject):
    shield: float
    SHIELD: float

    def __init__(self, *args, shield=None, **kwargs):
        super().__init__(*args, **kwargs)
        if shield is None:
            shield = self.SHIELD
        self.shield = shield

    def apply_damage(self, dmg: float):
        if self.shield is not None:
            d = min(self.shield, dmg)
            self.shield -= d
            dmg -= d
        super().apply_damage(dmg)

    def heal_shield(self, heal: float):
        if self.shield is not None:
            self.shield = min(self.shield + heal, self.SHIELD)

    def update(self, dt: float):
        super().update(dt)
        self.heal_shield(dt / 1000 * 2)


class HasHitpoints(MovingObject):
    hp: float
    HP: float

    def __init__(self, *args, hp=None, **kwargs):
        super().__init__(*args, **kwargs)
        if hp is None:
            hp = self.HP
        self.hp = hp

    def apply_damage(self, dmg: float):
        self.hp -= dmg
        if self.hp <= 0:
            self.mark_dead()
        super().apply_damage(dmg)

    def heal_hp(self, heal: float):
        self.hp = min(self.hp + heal, self.HP)
        super().heal_hp(heal)


class HasTimer(MovingObject):
    ttl: int
    TTL: int

    def __init__(self, *args, ttl=None, **kwargs):
        if ttl is None:
            ttl = self.TTL
        self.ttl = ttl
        super().__init__(*args, **kwargs)

    def update(self, dt: float):
        if self.alive_time >= self.ttl:
            self.mark_dead()
        super().update(dt)


class NoControl:
    def get_accels(self):
        return Vector3(0.0, 0.0, 0.0)


def _circle():
    surface = pg.surface.Surface((10, 10))
    pg.draw.circle(surface, WHITE, (5, 5), 5)
    return surface


class DebugArtifact(NoControl, StaticDrawable):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0
    IMAGE = CachedSurface(_circle())
