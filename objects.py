from __future__ import annotations
import pygame

from groups import ALL_SPRITES
from math_utils import (
    normalize_pos3,
    range_kutta_2,
    internal_coord_to_xy,
)
from consts import WHITE, GREEN, RED, ALL_SHIFTS, SCREEN_HEIGHT, SCREEN_WIDTH
from pygame.math import Vector3, Vector2
from collisions import ALL_SPRITES_CD


class MovingObject(pygame.sprite.Sprite):
    DRAG = 1 / 1000
    ANGULAR_DRAG = 2 / 1000
    TTL = None
    HP = None
    IMAGE = None

    image: pygame.Surface
    images: list[pygame.Surface]
    rect: pygame.Rect
    pos: Vector3
    speed: Vector3
    mass: float
    ttl: float | None
    hp: float | None
    alive: bool

    def __init__(self, *args, image=None, init_pos, init_speed, **kwargs):
        super().__init__(*args, **kwargs)
        print("creating", self)

        if image is None:
            image = self.IMAGE
        self.images = [pygame.transform.rotate(image, i) for i in range(360)]
        self.masks = [pygame.mask.from_surface(im) for im in self.images]

        self.pos = normalize_pos3(Vector3(init_pos))
        self.speed = Vector3(init_speed)

        self.update_image_rect()
        self._acc = Vector2()
        self._drag = Vector2()
        self.mass = self.MASS
        self.add(ALL_SPRITES)
        self.ttl = self.TTL
        self.hp = self.HP
        ALL_SPRITES_CD.add(self)
        self.alive = self.get_alive()

    def kill(self):
        ALL_SPRITES_CD.remove(self)
        print("kill", self)
        super().kill()

    def apply_damage(self, dmg: float):
        if self.hp is not None:
            self.hp -= dmg

    def on_collision(self, other: MovingObject):
        pass

    def draw_ui(self, target: pygame.Surface) -> list[pygame.Rect]:
        assert (
            target.get_width() == SCREEN_WIDTH and target.get_height() == SCREEN_HEIGHT
        )
        all_changes = []
        rect: pygame.Rect = self.images[0].get_rect(center=self.rect.center)
        rect2 = pygame.Rect(0, 0, 50, 5)
        rect2.midbottom = rect.midtop
        all_changes.append(pygame.draw.rect(target, GREEN, rect2, width=1))
        rect2.width = rect2.width * (self.hp / self.HP)
        all_changes.append(pygame.draw.rect(target, GREEN, rect2))
        return all_changes

    def get_alive(self) -> bool:
        return (self.ttl is None or self.ttl > 0.0) and (self.hp is None or self.hp > 0)

    @property
    def pos_xy(self) -> Vector2:
        return Vector2(self.pos.x, self.pos.y)

    @property
    def speed_xy(self) -> Vector2:
        return Vector2(self.speed.x, self.speed.y)

    def draw_debugs(self, target: pygame.Surface) -> list[pygame.Rect]:
        assert (
            target.get_width() == SCREEN_WIDTH and target.get_height() == SCREEN_HEIGHT
        )
        pos_xy = self.pos_xy
        speed_xy = self.speed_xy
        all_changes = []
        for shift in ALL_SHIFTS:
            dt = 200
            all_changes.append(
                pygame.draw.line(
                    target,
                    WHITE,
                    shift + pos_xy,
                    shift + pos_xy + dt * speed_xy,
                    1,
                )
            )
            dt = 200000
            all_changes.append(
                pygame.draw.line(
                    target,
                    GREEN,
                    shift + pos_xy,
                    shift + pos_xy + dt * self._acc,
                    1,
                )
            )
            all_changes.append(
                pygame.draw.line(
                    target,
                    RED,
                    shift + pos_xy + dt * self._acc,
                    shift + pos_xy + dt * self._acc - dt * self._drag,
                    1,
                )
            )
        return all_changes

    def update_image_rect(self):
        self.image = self.images[int(self.pos.z)]
        self.rect = self.image.get_rect(center=self.pos_xy)
        self.mask = self.masks[int(self.pos.z)]

    def update(self, dt: float):
        if not self.alive:
            return
        self.update_pos(dt)
        old_rect = self.rect
        self.update_image_rect()
        ALL_SPRITES_CD.move(self, self.rect, old_rect)
        if self.ttl is not None:
            self.ttl -= dt
        self.alive = self.get_alive()
        if not self.alive:
            self.on_death()
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
