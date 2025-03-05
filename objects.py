from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pygame as pg
from pygame.math import Vector2, Vector3

from config import CONFIG
from consts import (
    ALL_SHIFTS,
    BLACK,
    CYAN,
    RED,
    WHITE,
)
from groups import (
    ALL_COLLIDING_OBJECTS,
    ALL_DRAWABLE_OBJECTS,
    ALL_UI_DRAWABLE_OBJECTS,
    ALL_WITH_UPDATE,
    GroupWithCD,
)
from math_utils import (
    internal_coord_to_xy,
    normalize_pos3,
    range_kutta_2,
)
from postprocessing import with_outline
from teams import get_team_color

if TYPE_CHECKING:
    from surface import CachedAnimation, CachedSurface

import contextlib

from display import ALL_CHANGES_DISPLAYSURF, DISPLAYSURF
from surface import CachedSurface


class Object(pg.sprite.Sprite):
    alive_time: float
    alive_state: bool
    pos: Vector3
    all_statuses: pg.sprite.Group
    attachments: pg.sprite.Group

    def __init__(self, *args, init_pos, owner=None, **kwargs):
        assert not kwargs, f"{kwargs}"
        super().__init__()
        self.pos = normalize_pos3(Vector3(init_pos))
        self.alive_state = True
        self.alive_time = 0.0
        if owner is None:
            owner = self
        self.owner = owner
        self.update_image_rect()
        self.all_statuses = pg.sprite.Group()
        self.attachments = pg.sprite.Group()
        self.add(ALL_WITH_UPDATE, *args)

    def kill(self):
        for status in self.all_statuses:
            status.kill()
        for attached in self.attachments:
            attached.kill()
        super().kill()

    def mark_dead(self):
        self.alive_state = False

    def update(self, dt: float):
        self.alive_time += dt
        super().update(dt)

    def on_death(self):
        pass

    @property
    def pos_xy(self) -> Vector2:
        return Vector2(self.pos.x, self.pos.y)


class Attached:
    def __init__(self, *args, init_rel_pos: Vector3, base_object: Object, **kwargs):
        self.base_object = base_object
        self.priority = getattr(self.base_object, "priority", 0)
        self.rel_pos = Vector3(init_rel_pos)
        super().__init__(
            self.base_object.attachments,
            *args,
            init_pos=self.get_pos(),
            **kwargs,
        )

    def get_pos(self):
        pos_xy = self.base_object.pos_xy + internal_coord_to_xy(
            Vector2(self.rel_pos.x, self.rel_pos.y),
            self.base_object.pos.z,
        )
        return Vector3(pos_xy.x, pos_xy.y, self.base_object.pos.z + self.rel_pos.z)

    def update_pos(self, dt: float):
        self.pos = self.get_pos()


class Stationary:
    def update_pos(self, dt: float):
        pass


class MovesAbstract:
    DRAG: float
    ANGULAR_DRAG: float
    speed: Vector3

    def __init__(self, *args, init_speed, **kwargs):
        self.speed = Vector3(init_speed)
        super().__init__(*args, **kwargs)

    def update_pos(self, dt: float):
        new_pos, new_speed = self.updated_pos(dt)
        self.pos = normalize_pos3(new_pos)
        self.speed = new_speed

    def get_accels(self) -> Vector3:
        return Vector3(0.0, 0.0, 0.0)

    @property
    def speed_xy(self) -> Vector2:
        return Vector2(self.speed.x, self.speed.y)

    def updated_pos(self, dt: float) -> tuple[Vector3, Vector3]:
        raise NotImplementedError


class Moves(MovesAbstract):
    def updated_pos(self, dt: float) -> tuple[Vector3, Vector3]:
        all_accel = self.get_accels()

        def f(pos: Vector3, speed: Vector3):
            acc = internal_coord_to_xy(Vector2(all_accel.x, all_accel.y), pos.z)
            angular_drag = speed.z * abs(speed.z) * self.ANGULAR_DRAG
            speed_xy = Vector2(speed.x, speed.y)
            # |drag| = self.DRAG * |speed|**2
            drag = speed_xy.length() * self.DRAG * speed_xy
            acc -= drag
            return speed, Vector3(acc.x, acc.y, all_accel.z - angular_drag)

        return range_kutta_2(f, self.pos, self.speed, dt)


class MovesSimplified(MovesAbstract):
    def updated_pos(self, dt: float) -> tuple[Vector3, Vector3]:
        return self.pos + self.speed * dt, self.speed


class DrawableObject:
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
        super().__init__(*args, **kwargs)

        rect = self.rect
        x_start_a = rect.left // CONFIG.WORLD_WIDTH
        x_end_a = rect.right // CONFIG.WORLD_WIDTH
        y_start_a = rect.top // CONFIG.WORLD_HEIGHT
        y_end_a = rect.bottom // CONFIG.WORLD_HEIGHT
        for x in range(x_start_a, x_end_a + 1):
            for y in range(y_start_a, y_end_a + 1):
                self.add(
                    ALL_DRAWABLE_OBJECTS[
                        (-x * CONFIG.WORLD_WIDTH, -y * CONFIG.WORLD_HEIGHT)
                    ],
                )

    def get_surface(self) -> CachedSurface:
        raise NotImplementedError

    def update_image_rect(self):
        surf = self.get_surface()

        self.rect = surf.get_rect(
            self.pos.z,
            topleft=self.pos_xy - surf.get_centroid(self.pos.z),
        )
        self.mask = surf.get_mask(self.pos.z)
        self.image = surf.get_image(self.pos.z)

        with contextlib.suppress(AttributeError):
            self.image = self.with_postprocessing()

    def with_postprocessing(self):
        print(self, "with_postprocessing outline")
        return with_outline(self, get_team_color(self))

    def update(self, dt: float):
        super().update(dt)
        old_rect = self.rect
        old_pos = self.pos
        self.update_pos(dt)
        new_pos = self.pos
        if (
            int(old_pos.x) == int(new_pos.x)
            and int(old_pos.y) == int(new_pos.y)
            and int(old_pos.z) == int(new_pos.z)
            and isinstance(self, StaticDrawable)
        ):
            return

        self.update_image_rect()

        new_rect = self.rect

        for group in self.groups():
            if isinstance(group, GroupWithCD):
                group.cd.move(self, new_rect, old_rect)

        x_start_a = new_rect.left // CONFIG.WORLD_WIDTH
        x_end_a = new_rect.right // CONFIG.WORLD_WIDTH
        y_start_a = new_rect.top // CONFIG.WORLD_HEIGHT
        y_end_a = new_rect.bottom // CONFIG.WORLD_HEIGHT
        x_start_b = old_rect.left // CONFIG.WORLD_WIDTH
        x_end_b = old_rect.right // CONFIG.WORLD_WIDTH
        y_start_b = old_rect.top // CONFIG.WORLD_HEIGHT
        y_end_b = old_rect.bottom // CONFIG.WORLD_HEIGHT
        if (
            x_start_a == x_start_b
            and x_end_a == x_end_b
            and y_start_a == y_start_b
            and y_end_a == y_end_b
        ):
            return
        for x in range(x_start_b, x_end_b + 1):
            for y in range(y_start_b, y_end_b + 1):
                if x_start_a <= x <= x_end_a and y_start_a <= y <= y_end_a:
                    continue
                self.remove(
                    ALL_DRAWABLE_OBJECTS[
                        (-x * CONFIG.WORLD_WIDTH, -y * CONFIG.WORLD_HEIGHT)
                    ],
                )
        for x in range(x_start_a, x_end_a + 1):
            for y in range(y_start_a, y_end_a + 1):
                if x_start_b <= x <= x_end_b and y_start_b <= y <= y_end_b:
                    continue
                self.add(
                    ALL_DRAWABLE_OBJECTS[
                        (-x * CONFIG.WORLD_WIDTH, -y * CONFIG.WORLD_HEIGHT)
                    ],
                )


class StaticDrawable(DrawableObject):
    _image: CachedSurface

    def get_surface(self) -> CachedSurface:
        return self._image


class AnimatedDrawable(DrawableObject):
    _image: CachedAnimation

    def get_surface(self) -> CachedSurface:
        return self._image.get_frame(self.alive_time)


class DrawsUI:
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
                    pg.draw.rect(DISPLAYSURF, color, bar, width=1),
                )
                bar.width = bar.width * fill
                ALL_CHANGES_DISPLAYSURF.append(pg.draw.rect(DISPLAYSURF, color, bar))
                return _rect

            if isinstance(self, HasHitpoints):
                rect = draw_bar(RED, self.hp / self.HP, rect)
            if isinstance(self, HasShield):
                rect = draw_bar(CYAN, self.shield / self.SHIELD, rect)

            first = True
            for status in self.all_statuses:
                icon: pg.Surface = status.icon
                if first:
                    rect = icon.get_rect(bottomleft=rect.topleft)
                else:
                    rect = icon.get_rect(bottomleft=rect.bottomright)
                ALL_CHANGES_DISPLAYSURF.append(DISPLAYSURF.blit(icon.get_image(), rect))
                first = False


class HasMass:
    mass: float
    MASS: float | None

    def __init__(self, *args, mass=None, **kwargs):
        if mass is None:
            mass = self.MASS
        self.mass = mass
        super().__init__(*args, **kwargs)


class Collides:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(ALL_COLLIDING_OBJECTS)

    def on_collision(self, other: Object):
        pass

    @property
    def inertia_moment(self):
        return self.get_surface().inertia_moment_coef * self.mass


class HasEngines(Moves):
    all_engines: pg.sprite.Group

    def __init__(self, *args, **kwargs):
        self.all_engines = pg.sprite.Group()
        super().__init__(*args, **kwargs)

    def kill(self):
        for engine in self.all_engines:
            engine.kill()
        super().kill()

    def get_accels(self) -> Vector3:
        thrust = super().get_accels()
        for engine in self.all_engines:
            impulse = Vector2(
                0,
                -pg.math.clamp(engine.active, 0.0, 1.0) * engine.strength / 1000,
            ).rotate(
                engine.pos.z,
            )
            impulse_ = Vector3(impulse.x, impulse.y, 0)
            thrust += impulse_ / self.mass - impulse_.cross(
                Vector3(engine.pos.x, engine.pos.y, 0),
            ) / self.inertia_moment * math.degrees(1)

        return thrust


class HasHitpoints:
    hp: float
    HP: float

    def __init__(self, *args, hp=None, **kwargs):
        if hp is None:
            hp = self.HP
        self.hp = hp
        super().__init__(*args, **kwargs)

    def apply_damage(self, dmg: float):
        self.hp -= dmg
        if self.hp <= 0:
            self.mark_dead()
        with contextlib.suppress(AttributeError):
            super().apply_damage(dmg)

    def heal_hp(self, heal: float):
        self.hp = min(self.hp + heal, self.HP)


class HasShield(HasHitpoints):
    shield: float
    SHIELD: float

    def __init__(self, *args, shield=None, **kwargs):
        if shield is None:
            shield = self.SHIELD
        self.shield = shield
        super().__init__(*args, **kwargs)

    def apply_damage(self, dmg: float):
        d = min(self.shield, dmg)
        self.shield -= d
        dmg -= d
        super().apply_damage(dmg)

    def heal_shield(self, heal: float):
        self.shield = min(self.shield + heal, self.SHIELD)

    def update(self, dt: float):
        super().update(dt)
        self.heal_shield(dt / 1000 * 2)


class HasTimer:
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


def _circle():
    surface = pg.surface.Surface((10, 10))
    pg.draw.circle(surface, WHITE, (5, 5), 5)
    return surface


class DebugArtifact(StaticDrawable):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0
    IMAGE = CachedSurface(_circle())
