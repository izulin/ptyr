from __future__ import annotations
import math
import pygame
import numpy as np
from math_utils import normalize_pos, range_kutta_4
from consts import WHITE, GREEN, RED


def internal_coord_to_xy(forward_pos, side_pos, ang):
    radians = 2 * np.pi * ang / 360
    sinr = math.sin(radians)
    cosr = math.cos(radians)
    return np.array(
        [-forward_pos * sinr - side_pos * cosr, -forward_pos * cosr + side_pos * sinr]
    )


class MovingObject(pygame.sprite.Sprite):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = FORWARD_THRUST
    ANGULAR_THRUST = 0.2 / 1000
    DRAG = 1 / 1000
    ANGULAR_DRAG = ANGULAR_THRUST / 0.3**2

    def __init__(self, *args, image, init_pos, init_speed, **kwargs):
        super().__init__(*args, **kwargs)

        self._image = image

        self.pos = np.concatenate([normalize_pos(init_pos[:2]), [init_pos[2] % 360]])
        self.speed = np.array(init_speed)

        self.update_image_rect()
        self._acc = np.array((0.0, 0.0))
        self._drag = np.array((0.0, 0.0))

    @property
    def mass(self):
        raise NotImplementedError

    def draw_debugs(self, target: pygame.Surface):
        for a, b in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]:
            shift = np.array([target.get_width() * a, target.get_height() * b])
            dt = 200
            pygame.draw.line(
                target,
                WHITE,
                shift + self.pos[:2],
                shift + self.pos[:2] + dt * self.speed[:2],
                1,
            )
            dt = 200000
            pygame.draw.line(
                target,
                GREEN,
                shift + self.pos[:2],
                shift + self.pos[:2] + dt * self._acc,
                1,
            )
            pygame.draw.line(
                target,
                RED,
                shift + self.pos[:2] + dt * self._acc,
                shift + self.pos[:2] + +dt * self._acc - dt * self._drag,
                1,
            )

    def update_image_rect(self):
        self.image = pygame.transform.rotate(self._image, self.pos[2] % 360)
        self.rect = self.image.get_rect(center=normalize_pos(self.pos[:2]))

    def update(self, dt: float):
        self.update_pos(dt)
        self.update_image_rect()

    def get_accels(self):
        raise NotImplementedError

    def update_pos(self, dt: float):
        forward_accel, angular_accel, side_accel = self.get_accels()

        def f(pos_speed):
            pos = pos_speed[0:3]
            speed = pos_speed[3:6]

            self._acc = internal_coord_to_xy(forward_accel, side_accel, pos[2])
            angular_drag = (speed[2] ** 2) * np.sign(speed[2]) * self.ANGULAR_DRAG

            speed_squared = np.dot(speed[:2], speed[:2])

            if speed_squared > 0:
                # |drag| = self.DRAG * |speed|**2
                self._drag = math.sqrt(speed_squared) * self.DRAG * speed[:2]
            else:
                self._drag = np.array([0.0, 0.0])

            acc = np.concatenate(
                [self._acc - self._drag, [angular_accel - angular_drag]]
            )

            return np.concatenate([speed, acc])

        new_pos_speed = range_kutta_4(f, np.concatenate([self.pos, self.speed]), dt)

        self.pos = new_pos_speed[0:3]
        self.speed = new_pos_speed[3:6]

        self.pos = np.concatenate([normalize_pos(self.pos[:2]), [self.pos[2] % 360]])


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
