from __future__ import annotations
from consts import SCREEN_HEIGHT, SCREEN_WIDTH
from typing import TYPE_CHECKING
from pygame.math import Vector2, Vector3
import pygame as pg
import math
import random

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


def bounding_rect(mask: pg.Mask) -> pg.Rect:
    bounding_rects = mask.get_bounding_rects()
    return bounding_rects[0].unionall(bounding_rects[1:])


def get_from_mask(mask: pg.Mask):
    br = bounding_rect(mask)
    cnt = mask.count()

    while br.width > 1 or br.height > 1:
        if br.width > br.height:
            midpoint = (br.left + br.right) // 2
            submask = pg.Mask((midpoint - br.left, br.height), fill=True)
        else:
            midpoint = (br.top + br.bottom) // 2
            submask = pg.Mask((br.width, midpoint - br.top), fill=True)
        sub_cnt = mask.overlap_area(submask, br.topleft)
        if random.uniform(0, 1) < sub_cnt / cnt:
            mask = mask.overlap_mask(submask, br.topleft)
        else:
            mask.erase(submask, br.topleft)
        br = bounding_rect(mask)
        cnt = mask.count()

    return Vector2(br.x, br.y)


def get_collision_point(a: MovingObject, b: MovingObject) -> Vector2:
    x_diff = b.rect.x - a.rect.x
    y_diff = b.rect.y - a.rect.y
    overlap_mask: pg.Mask = a.mask.overlap_mask(b.mask, (x_diff, y_diff))

    return get_from_mask(overlap_mask) + Vector2(a.rect.x, a.rect.y)


def collide_objects(
    a: MovingObject, b: MovingObject, collision_point: Vector2, elasticity=0.75
) -> float:
    a_r: Vector2 = collision_point - a.pos_xy
    b_r: Vector2 = collision_point - b.pos_xy

    a_local_speed = a.speed_xy + a_r.rotate(90) * math.radians(a.speed.z)
    b_local_speed = b.speed_xy + b_r.rotate(90) * math.radians(b.speed.z)

    local_speed_diff = a_local_speed - b_local_speed

    normal = a_r.normalize() - b_r.normalize()

    if normal * local_speed_diff >= 0:
        return 0.0

    impulse_direction: Vector2 = local_speed_diff.normalize()

    a_inertia = (
        1 / a.mass + a_r.project(impulse_direction).length_squared() / a.inertia_moment
    )

    b_inertia = (
        1 / b.mass + b_r.project(impulse_direction).length_squared() / b.inertia_moment
    )

    impulse: Vector2 = local_speed_diff.project(impulse_direction) / (
        a_inertia + b_inertia
    )
    a_dspeed = Vector3(
        impulse.x / a.mass,
        impulse.y / a.mass,
        0,
    ) + Vector3(
        impulse.x, impulse.y, 0
    ).cross(Vector3(a_r.x, a_r.y, 0)) / a.inertia_moment * math.degrees(1)
    b_dspeed = -Vector3(impulse.x / b.mass, impulse.y / b.mass, 0) - Vector3(
        impulse.x, impulse.y, 0
    ).cross(Vector3(b_r.x, b_r.y, 0)) / b.inertia_moment * math.degrees(1)

    E = (
        a.speed.x**2 * a.mass
        + a.speed.y**2 * a.mass
        + math.radians(a.speed.z) ** 2 * a.inertia_moment
        + b.speed.x**2 * b.mass
        + b.speed.y**2 * b.mass
        + math.radians(b.speed.z) ** 2 * b.inertia_moment
    )

    A = (
        a_dspeed.x**2 * a.mass
        + a_dspeed.y**2 * a.mass
        + b_dspeed.x**2 * b.mass
        + b_dspeed.y**2 * b.mass
        + math.radians(a_dspeed.z) ** 2 * a.inertia_moment
        + math.radians(b_dspeed.z) ** 2 * b.inertia_moment
    )
    B = (
        a_dspeed.x * a.speed.x * a.mass
        + a_dspeed.y * a.speed.y * a.mass
        + b_dspeed.x * b.speed.x * b.mass
        + b_dspeed.y * b.speed.y * b.mass
        + math.radians(a_dspeed.z) * math.radians(a.speed.z) * a.inertia_moment
        + math.radians(b_dspeed.z) * math.radians(b.speed.z) * b.inertia_moment
    )

    # if B<0:
    #    return 0.0

    t = -2 * B / A
    print("E", E, "t", t)

    # print(a.speed, b.speed)

    a.speed += t * a_dspeed * (1 + elasticity) / 2
    b.speed += t * b_dspeed * (1 + elasticity) / 2

    # print(a.speed, b.speed)
    return B**2 / A


def internal_coord_to_xy(pos: Vector2, ang: float) -> Vector2:
    return Vector2(pos.x, -pos.y).rotate(-ang)
