from __future__ import annotations
from consts import SCREEN_HEIGHT, SCREEN_WIDTH
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sprite import MovingObject

def range_kutta_4(f, y, dt):
    k1 = f(y)
    k2 = f(y + dt / 2 * k1)
    k3 = f(y + dt / 2 * k2)
    k4 = f(y + dt * k3)

    return y + (k1 + 2 * k2 + 2 * k3 + k4) * dt / 6

def range_kutta_1(f, y, dt):
    return y + f(y) * dt

def normalize_pos(pos):
    pos = pos[:]
    pos[0] %= SCREEN_WIDTH
    pos[0] += SCREEN_WIDTH
    pos[1] %= SCREEN_HEIGHT
    pos[1] += SCREEN_HEIGHT
    return pos

def test_if_proper_collision(a: MovingObject, b: MovingObject):
    pos_diff = a.pos[:2] - b.pos[:2]
    speed_diff = a.speed[:2] - b.speed[:2]
    return pos_diff[0]*speed_diff[0] + pos_diff[1]*speed_diff[1] < 0

def collide_objects(a: MovingObject, b: MovingObject):
    pos_diff = a.pos[:2] - b.pos[:2]
    center_mass_speed = (a.speed[:2]*a.mass + b.speed[:2]*b.mass)/(a.mass+b.mass)
    a_speed_norm = a.speed[:2] - center_mass_speed
    b_speed_norm = b.speed[:2] - center_mass_speed
    a_proj = (a_speed_norm[0] * pos_diff[0] + a_speed_norm[1] * pos_diff[1]) / (pos_diff[0]**2 + pos_diff[1]**2) * pos_diff
    b_proj = (b_speed_norm[0] * pos_diff[0] + b_speed_norm[1] * pos_diff[1]) / (pos_diff[0]**2 + pos_diff[1]**2) * pos_diff
    ELASTICITY = 1.0
    a.speed[:2] -= (1.0+ELASTICITY)*a_proj
    b.speed[:2] -= (1.0+ELASTICITY)*b_proj