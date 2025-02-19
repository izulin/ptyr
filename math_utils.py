from __future__ import annotations

from consts import SCREEN_HEIGHT, SCREEN_WIDTH
from typing import TYPE_CHECKING
from pygame.math import Vector2, Vector3

if TYPE_CHECKING:
    pass


def range_kutta_4(f, x, y, dt):
    h1, k1 = f(x, y)
    h2, k2 = f(x + dt / 2 * h1, y + dt / 2 * k1)
    h3, k3 = f(x + dt / 2 * h2, y + dt / 2 * k2)
    h4, k4 = f(x + dt * h3, y + dt * k3)
    return (
        x + (h1 + 2 * h2 + 2 * h3 + h4) * dt / 6,
        y + (k1 + 2 * k2 + 2 * k3 + k4) * dt / 6,
    )


def range_kutta_1(f, x, y, dt):
    h1, k1 = f(x, y)
    return x + dt * h1, y + dt * k1


def range_kutta_2(f, x, y, dt):
    h1, k1 = f(x, y)
    h2, k2 = f(x + dt * h1, y + dt * k1)
    return x + (h1 + h2) * dt / 2, y + (k1 + k2) * dt / 2


def normalize_pos2(pos: Vector2):
    return Vector2(pos.x % SCREEN_WIDTH, pos.y % SCREEN_HEIGHT)


def normalize_pos3(pos: Vector3):
    return Vector3(pos.x % SCREEN_WIDTH, pos.y % SCREEN_HEIGHT, pos.z % 360)


def internal_coord_to_xy(pos: Vector2, ang: float) -> Vector2:
    return Vector2(pos.x, -pos.y).rotate(-ang)
