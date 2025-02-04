from __future__ import annotations
from consts import SCREEN_HEIGHT, SCREEN_WIDTH
from typing import TYPE_CHECKING
from pygame.math import Vector2, Vector3

if TYPE_CHECKING:
    from object import MovingObject


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


def test_if_proper_collision(a: MovingObject, b: MovingObject):
    pos_diff = a.pos_xy - b.pos_xy
    speed_diff = a.speed_xy - b.speed_xy
    return pos_diff * speed_diff < 0


def collide_objects(a: MovingObject, b: MovingObject, elasticity=1.0):
    pos_diff = a.pos_xy - b.pos_xy
    center_mass_speed = (a.speed_xy * a.mass + b.speed_xy * b.mass) / (a.mass + b.mass)
    a_speed_norm = a.speed_xy - center_mass_speed
    b_speed_norm = b.speed_xy - center_mass_speed
    a_proj = (a_speed_norm * pos_diff) / (pos_diff * pos_diff) * pos_diff
    b_proj = (b_speed_norm * pos_diff) / (pos_diff * pos_diff) * pos_diff
    a_new_speed_xy = a.speed_xy - (1.0 + elasticity) * a_proj
    b_new_speed_xy = b.speed_xy - (1.0 + elasticity) * b_proj
    a.speed = Vector3(a_new_speed_xy.x, a_new_speed_xy.y, a.speed.z)
    b.speed = Vector3(b_new_speed_xy.x, b_new_speed_xy.y, b.speed.z)


def internal_coord_to_xy(forward_pos, side_pos, ang):
    return Vector2(-side_pos, -forward_pos).rotate(-ang)
