from __future__ import annotations
from consts import SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from typing import TYPE_CHECKING
from pygame.math import Vector2, Vector3
import pygame as pg

if TYPE_CHECKING:
    from objects import MovingObject


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
    return True
    pos_diff = a.pos_xy - b.pos_xy
    speed_diff = a.speed_xy - b.speed_xy
    return pos_diff * speed_diff < 0


def get_collision_point(a: MovingObject, b: MovingObject) -> Vector2:
    x_diff = b.rect.x - a.rect.x
    y_diff = b.rect.y - a.rect.y
    overlap_mask: pg.Mask = a.mask.overlap_mask(b.mask, (x_diff, y_diff))
    bounding_rects: list[pg.Rect] = overlap_mask.get_bounding_rects()
    x_mid = (
        min(rect.left for rect in bounding_rects)
        + max(rect.right for rect in bounding_rects)
        - 1
    ) / 2
    y_mid = (
        min(rect.top for rect in bounding_rects)
        + max(rect.bottom for rect in bounding_rects)
        - 1
    ) / 2
    return Vector2(a.rect.x + x_mid, a.rect.y + y_mid)


def collide_objects(
    a: MovingObject, b: MovingObject, collision_point: Vector2, elasticity=0.75
) -> float:
    a_r: Vector2 = collision_point - a.pos_xy
    b_r: Vector2 = collision_point - b.pos_xy

    a_local_speed = a.speed_xy + a_r.rotate(90) * a.speed.z * 3.14 / 180
    b_local_speed = b.speed_xy + b_r.rotate(90) * b.speed.z * 3.14 / 180

    local_speed_diff = a_local_speed - b_local_speed

    normal = (a.pos_xy - collision_point).normalize() - (
        b.pos_xy - collision_point
    ).normalize()

    if normal * local_speed_diff >= 0:
        return 0.0

    impulse_direction: Vector2 = local_speed_diff.normalize()

    a_proj = a_local_speed.project(impulse_direction)
    b_proj = b_local_speed.project(impulse_direction)
    a_inertia = (
        1 / a.mass + a_r.project(impulse_direction).length_squared() / a.inertia_moment
    )

    b_inertia = (
        1 / b.mass + b_r.project(impulse_direction).length_squared() / b.inertia_moment
    )

    impulse: Vector2 = (a_proj - b_proj) / (a_inertia + b_inertia)
    a_dspeed = Vector3(
        *(impulse / a.mass),
        Vector3(*impulse, 0).cross(Vector3(*a_r, 0)).z / a.inertia_moment * 180 / 3.14,
    )
    b_dspeed = -Vector3(
        *(impulse / b.mass),
        Vector3(*impulse, 0).cross(Vector3(*b_r, 0)).z / b.inertia_moment * 180 / 3.14,
    )
    A = (
        a_dspeed.x**2 * a.mass
        + a_dspeed.y**2 * a.mass
        + b_dspeed.x**2 * b.mass
        + b_dspeed.y**2 * b.mass
        + a_dspeed.z**2 * (3.14 / 180) ** 2 * a.inertia_moment
        + b_dspeed.z**2 * (3.14 / 180) ** 2 * b.inertia_moment
    )
    B = (
        a_dspeed.x * a.speed.x * a.mass
        + a_dspeed.y * a.speed.y * a.mass
        + b_dspeed.x * b.speed.x * b.mass
        + b_dspeed.y * b.speed.y * b.mass
        + a_dspeed.z * a.speed.z * (3.14 / 180) ** 2 * a.inertia_moment
        + b_dspeed.z * b.speed.z * (3.14 / 180) ** 2 * b.inertia_moment
    )

    t = -2 * B / A

    a.speed += t * a_dspeed * (1 + elasticity) / 2
    b.speed += t * b_dspeed * (1 + elasticity) / 2

    return B**2 / A


def internal_coord_to_xy(pos: Vector2, ang: float) -> Vector2:
    return Vector2(pos.x, -pos.y).rotate(-ang)
