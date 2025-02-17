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
    pos_diff = a.pos_xy - b.pos_xy
    speed_diff = a.speed_xy - b.speed_xy
    return pos_diff * speed_diff < 0


def collide_objects(a: MovingObject, b: MovingObject, elasticity=0.9) -> float:
    # xoffset = b.rect[0] - a.rect[0]
    # yoffset = b.rect[1] - a.rect[1]
    # overlap_mask: pg.Mask = a.mask.overlap_mask(b.mask, (xoffset, yoffset))
    # bounding_rects: list[pg.Rect] = overlap_mask.get_bounding_rects()
    # x_mid = (min(rect.left for rect in bounding_rects) + max(rect.right for rect in bounding_rects) - 1)/2
    # y_mid = (min(rect.top for rect in bounding_rects) + max(rect.bottom for rect in bounding_rects) - 1)/2
    # collision_point = Vector2(a.rect.x+x_mid, a.rect.y+y_mid)

    pos_diff = a.pos_xy - b.pos_xy
    a_proj = a.speed_xy.project(pos_diff)
    b_proj = b.speed_xy.project(pos_diff)
    impulse: Vector2 = (a_proj - b_proj) / (1 / a.mass + 1 / b.mass)
    a.speed = Vector3(*(a.speed_xy - (1.0 + elasticity) * impulse / a.mass), a.speed.z)
    b.speed = Vector3(*(b.speed_xy + (1.0 + elasticity) * impulse / b.mass), b.speed.z)
    return impulse.length()


def internal_coord_to_xy(pos: Vector2, ang: float) -> Vector2:
    return Vector2(pos.x, -pos.y).rotate(-ang)
