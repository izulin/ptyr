from __future__ import annotations
import pygame
from math_utils import (
    normalize_pos2,
    normalize_pos3,
    range_kutta_1,
    range_kutta_4,
    range_kutta_2,
    internal_coord_to_xy,
)
from consts import WHITE, GREEN, RED, ALL_SHIFTS, SCREEN_HEIGHT, SCREEN_WIDTH
from pygame.math import Vector3, Vector2


class MovingObject(pygame.sprite.Sprite):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = FORWARD_THRUST
    ANGULAR_THRUST = 0.2 / 1000
    DRAG = 1 / 1000
    ANGULAR_DRAG = ANGULAR_THRUST / 0.3**2

    image: pygame.Surface
    images: list[pygame.Surface]
    rect: pygame.Rect
    pos: Vector3
    speed: Vector3

    def __init__(self, *args, image, init_pos, init_speed, **kwargs):
        super().__init__(*args, **kwargs)

        self.images = [pygame.transform.rotate(image, i) for i in range(360)]
        self.masks = [pygame.mask.from_surface(im) for im in self.images]

        self.pos = normalize_pos3(Vector3(init_pos))
        self.speed = Vector3(init_speed)

        self.update_image_rect()
        self._acc = Vector2()
        self._drag = Vector2()

    @property
    def mass(self):
        raise NotImplementedError

    @property
    def pos_xy(self):
        return Vector2(self.pos.x, self.pos.y)

    @property
    def speed_xy(self):
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

    controls: dict[str, int]

    def __init__(self, *args, controls, **kwargs):
        super().__init__(*args, **kwargs)
        self.controls = controls

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

    @property
    def mass(self):
        return 30.0


class Asteroid(MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def get_accels(self):
        return 0.0, 0.0, 0.0

    @property
    def mass(self):
        return 100.0
