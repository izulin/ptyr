from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg
import pygame.math
from pygame import Vector2

from display import DISPLAYSURF

if TYPE_CHECKING:
    from objects import Object


class Controller:
    owner: Object

    def __init__(self, owner):
        self.owner = owner

    def update(self, dt: float):
        raise NotImplementedError


def get_mouse_pos():
    screen_pos = pg.mouse.get_pos()
    screen_size = pg.display.get_surface().get_size()
    world_size = DISPLAYSURF.get_size()
    return (
        screen_pos[0] / screen_size[0] * world_size[0],
        screen_pos[1] / screen_size[1] * world_size[1],
    )


class StabilizerController(Controller):
    def update(self, dt: float):
        self.owner.back_engine.active = 1
        self.owner.back_left_engine.active = int(self.owner.speed.z <= 0)
        self.owner.back_right_engine.active = int(self.owner.speed.z >= 0)


class MouseTargetingController(Controller):
    def update(self, dt: float):
        target = Vector2(get_mouse_pos())
        own_pos = self.owner.pos_xy
        target_ang = 270 - (target - own_pos).as_polar()[1]
        speed_ang = 270 - self.owner.speed_xy.as_polar()[1]

        dest = target_ang + pg.math.clamp(target_ang - speed_ang, -30, 30)
        error = ((dest - self.owner.pos.z + 180) % 360 - 180) / 180 / 2
        prev_error = getattr(self, "prev_error", error)
        self.integral_error = (
            getattr(self, "integral_error", 0) * (0.5 ** (dt / 1000))
            + (dt / 1000) * error
        )
        self.prev_error = error
        d_error = (error - prev_error) / (dt / 1000)

        signal = error + d_error + self.integral_error

        self.owner.back_engine.active = (1 - abs(error)) ** 10
        self.owner.back_left_engine.active = 10 * signal
        self.owner.back_right_engine.active = -10 * signal
