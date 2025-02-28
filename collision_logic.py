from __future__ import annotations

import math
import random

import pygame as pg
from pygame import Vector2, Vector3

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from powerups import PowerUp
    from players import Player
    from objects import DrawableObject, Collides


def sample_from_mask(mask: pg.Mask):
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


def bounding_rect(mask: pg.Mask) -> pg.Rect:
    bounding_rects = mask.get_bounding_rects()
    return bounding_rects[0].unionall(bounding_rects[1:])


def get_collision_point(a: DrawableObject, b: DrawableObject) -> Vector2:
    x_diff = b.rect.x - a.rect.x
    y_diff = b.rect.y - a.rect.y
    overlap_mask: pg.Mask = a.mask.overlap_mask(b.mask, (x_diff, y_diff))

    return sample_from_mask(overlap_mask) + Vector2(a.rect.x, a.rect.y)


def collide_objects(
    a: Collides, b: Collides, collision_point: Vector2, elasticity=0.75
) -> float:
    a_r: Vector2 = collision_point - a.pos_xy
    b_r: Vector2 = collision_point - b.pos_xy

    a_local_speed = a.speed_xy + a_r.rotate(90) * math.radians(a.speed.z)
    b_local_speed = b.speed_xy + b_r.rotate(90) * math.radians(b.speed.z)

    local_speed_diff = a_local_speed - b_local_speed

    normal = (b_r.normalize() * 1.01 - a_r.normalize()).normalize()

    if normal * local_speed_diff >= 0:
        return 0.0

    impulse = local_speed_diff.project(normal)

    impulse_ = Vector3(
        impulse.x,
        impulse.y,
        0,
    )

    a_dspeed = impulse_ / a.mass + impulse_.cross(
        Vector3(a_r.x, a_r.y, 0)
    ) / a.inertia_moment * math.degrees(1)
    b_dspeed = -impulse_ / b.mass - impulse_.cross(
        Vector3(b_r.x, b_r.y, 0)
    ) / b.inertia_moment * math.degrees(1)

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

    t = -2 * B / A

    if t >= 0:
        return 0.0

    a.speed += t * a_dspeed * (1 + elasticity) / 2
    b.speed += t * b_dspeed * (1 + elasticity) / 2

    return B**2 / A


def _colliding_colliding_logic(obj_a: Collides, obj_b: Collides):
    if id(obj_b) < id(obj_a):
        return
    obj_a.on_collision(obj_b)
    obj_b.on_collision(obj_a)
    for _ in range(10):
        collision_point = get_collision_point(obj_a, obj_b)
        energy = collide_objects(obj_a, obj_b, collision_point)
        try:
            obj_a.apply_damage(100 * energy)
            obj_b.apply_damage(100 * energy)
        except AttributeError:
            pass


def _player_powerup_logic(player: Player, powerup: PowerUp):
    powerup.on_collision(player)
