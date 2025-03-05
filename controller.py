from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame as pg
from pygame import Vector2

from consts import ALL_SHIFTS
from groups import ALL_PLAYERS
from math_utils import internal_coord_to_xy

if TYPE_CHECKING:
    from objects import Object


class Controller:
    controlled: Object

    def __init__(self, controlled):
        self.controlled = controlled

    def update(self, dt: float):
        raise NotImplementedError


class StabilizerController(Controller):
    def update(self, dt: float):
        self.controlled.back_engine.active = 1
        self.controlled.back_left_engine.active = int(self.controlled.speed.z <= 0)
        self.controlled.back_right_engine.active = int(self.controlled.speed.z >= 0)


class PIDHomingController(Controller):
    def update(self, dt: float):
        for player in ALL_PLAYERS:
            if player != self.controlled.owner:
                target = player
                break
        else:
            self.controlled.back_engine.active = 0
            self.controlled.back_left_engine.active = 0
            self.controlled.back_right_engine.active = 0
            return

        best = math.inf, None
        for shift in ALL_SHIFTS:
            score = pg.Vector2.distance_to(
                self.controlled.pos_xy
                + self.controlled.speed_xy * 1000
                + internal_coord_to_xy(Vector2(0, 100), self.controlled.pos.z),
                target.pos_xy + shift,
            )
            best = min(best, (score, shift))
        _, best_shift = best

        target_vector = target.pos_xy + best_shift - self.controlled.pos_xy
        target_vector = target_vector.normalize()
        speed_vector = (self.controlled.speed_xy - target.speed_xy).normalize()
        ang = 270 - (target_vector + 2 * (target_vector - speed_vector)).as_polar()[1]

        error = ((ang - self.controlled.pos.z + 180) % 360 - 180) / 180 / 2
        prev_error = getattr(self, "prev_error", error)
        self.integral_error = (
            getattr(self, "integral_error", 0) * (0.1 ** (dt / 1000))
            + (dt / 1000) * error
        )
        self.prev_error = error
        d_error = (error - prev_error) / (dt / 1000)
        integral = pg.math.clamp(10 * self.integral_error, -0.1, 0.1)

        signal = error + d_error + integral

        self.controlled.back_engine.active = (1 - abs(error)) ** 10
        self.controlled.back_left_engine.active = 100 * signal
        self.controlled.back_right_engine.active = -100 * signal
