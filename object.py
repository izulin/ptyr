from __future__ import annotations
import pygame

from assets import AsteroidLargeImage, SmallPlasmaImage
from groups import ALL_SPRITES, ALL_PLAYERS, ALL_ASTEROIDS, ALL_BULLETS
from math_utils import (
    normalize_pos3,
    range_kutta_2,
    internal_coord_to_xy,
    embed,
)
from consts import WHITE, GREEN, RED, ALL_SHIFTS, SCREEN_HEIGHT, SCREEN_WIDTH
from pygame.math import Vector3, Vector2


class MovingObject(pygame.sprite.Sprite):
    DRAG = 1 / 1000
    ANGULAR_DRAG = 2 / 1000

    image: pygame.Surface
    images: list[pygame.Surface]
    rect: pygame.Rect
    pos: Vector3
    speed: Vector3
    mass: float
    ttl: float | None

    def __init__(self, *args, image, init_pos, init_speed, ttl=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.images = [pygame.transform.rotate(image, i) for i in range(360)]
        self.masks = [pygame.mask.from_surface(im) for im in self.images]

        self.pos = normalize_pos3(Vector3(init_pos))
        self.speed = Vector3(init_speed)

        self.update_image_rect()
        self._acc = Vector2()
        self._drag = Vector2()
        self.mass = self.MASS
        self.add(ALL_SPRITES)
        self.ttl = ttl

    @property
    def alive(self) -> bool:
        return self.ttl is None or self.ttl > 0.0

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
        self.update_pos(dt)
        self.update_image_rect()
        if self.ttl is not None:
            self.ttl -= dt
        if not self.alive:
            self.kill()

    def get_accels(self):
        raise NotImplementedError

    def update_pos(self, dt: float):
        forward_accel, angular_accel, side_accel = self.get_accels()

        def f(pos: Vector3, speed: Vector3):
            self._acc = internal_coord_to_xy(forward_accel, side_accel, pos.z)
            angular_drag = speed.z * abs(speed.z) * self.ANGULAR_DRAG

            speed_xy = Vector2(speed.x, speed.y)
            # |drag| = self.DRAG * |speed|**2
            self._drag = speed_xy.length() * self.DRAG * speed_xy

            acc_xy = self._acc - self._drag
            acc = Vector3(acc_xy.x, acc_xy.y, angular_accel - angular_drag)

            return speed, acc

        new_pos, new_speed = range_kutta_2(f, self.pos, self.speed, dt)

        self.pos = normalize_pos3(new_pos)
        self.speed = new_speed


class Player(MovingObject):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = 0.05 / 1000
    ANGULAR_THRUST = 0.2 / 1000

    MASS = 30.0

    controls: dict[str, int]
    weapon: Weapon

    def __init__(self, *args, controls, **kwargs):
        super().__init__(*args, **kwargs)
        self.controls = controls
        self.add(ALL_PLAYERS)
        self.weapon = Weapon(owner=self, cooldown=100, ammo=None)

    def get_accels(self) -> tuple[float, float, float]:
        pressed_keys = pygame.key.get_pressed()

        forward_accel = self.FORWARD_THRUST * (
            int(pressed_keys[self.controls["forward"]])
            - int(pressed_keys[self.controls["backward"]])
        )
        angular_accel = self.ANGULAR_THRUST * (
            int(pressed_keys[self.controls["left_turn"]])
            - int(pressed_keys[self.controls["right_turn"]])
        )
        side_accel = self.SIDE_THRUST * (
            int(pressed_keys[self.controls["left_strafe"]])
            - int(pressed_keys[self.controls["right_strafe"]])
        )

        return forward_accel, angular_accel, side_accel

    def update(self, dt: float):
        pressed_keys = pygame.key.get_pressed()
        self.weapon.update(dt)
        if pressed_keys[self.controls["shoot"]]:
            self.weapon.fire()
        # self.weapon.fire()
        super().update(dt)


class PassiveObject(MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def get_accels(self):
        return 0.0, 0.0, 0.0


class Asteroid(PassiveObject):
    MASS = 100.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, image=AsteroidLargeImage)
        self.add(ALL_ASTEROIDS)


class SmallPlasma(PassiveObject):
    MASS = 1.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, image=SmallPlasmaImage, ttl=10_000)
        self.add(ALL_BULLETS)


class Weapon:
    owner: Player
    cooldown: float
    ammo: int | None
    init_speed: float
    cooldown_left: float

    def __init__(self, *, owner, cooldown, ammo):
        self.owner = owner
        self.cooldown = cooldown
        self.ammo = ammo

        self.cooldown_left = 0.0

    def update(self, dt):
        self.cooldown_left -= dt

    def fire(self):
        if self.cooldown_left > 0:
            return
        if self.ammo is not None and self.ammo <= 0:
            return
        init_pos = self.owner.pos + embed(
            internal_coord_to_xy(20, 0, self.owner.pos[2]), 0.0
        )
        init_speed = self.owner.speed + embed(
            internal_coord_to_xy(0.3, 0, self.owner.pos[2]), 0.0
        )
        SmallPlasma(init_pos=init_pos, init_speed=init_speed)
        self.cooldown_left = self.cooldown
