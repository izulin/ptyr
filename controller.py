from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg
import pygame.math

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
        # target = Vector2(get_mouse_pos())
        from players import get_player

        target = get_player(3 - self.owner.owner.player_id)
        if target is None:
            return

        target_vector = target.pos_xy - self.owner.pos_xy
        target_vector = target_vector.normalize()
        speed_vector = (self.owner.speed_xy - target.speed_xy).normalize()
        ang = 270 - (target_vector + 2 * (target_vector - speed_vector)).as_polar()[1]

        error = ((ang - self.owner.pos.z + 180) % 360 - 180) / 180 / 2
        prev_error = getattr(self, "prev_error", error)
        self.integral_error = (
            getattr(self, "integral_error", 0) * (0.1 ** (dt / 1000))
            + (dt / 1000) * error
        )
        self.prev_error = error
        d_error = (error - prev_error) / (dt / 1000)

        signal = error + d_error + 0.1 * error / abs(error)  # self.integral_error

        self.owner.back_engine.active = (1 - abs(error)) ** 10
        self.owner.back_left_engine.active = 100 * signal
        self.owner.back_right_engine.active = -100 * signal
