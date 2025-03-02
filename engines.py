from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pygame as pg
from pygame import Vector2, Vector3

from groups import ALL_WITH_UPDATE
from math_utils import internal_coord_to_xy
from particles import Particle

if TYPE_CHECKING:
    from objects import Object


class Engine(pg.sprite.Sprite):
    def __init__(self, owner: Object, pos: Vector3, strength: float):
        super().__init__(ALL_WITH_UPDATE)
        self.pos = pos
        self.cooldown = 0.0
        self.strength = strength
        self.owner = owner
        self.active = 0
        self.owner.all_engines.add(self)

    def update(self, dt: float):
        if self.cooldown >= 0.0:
            self.cooldown -= dt
        ANGLE_SPREAD = 10
        WIDTH = 1.0
        self.active = min(1.0, self.active)
        self.active = max(0.0, self.active)
        PARTICLE_SPEED = math.sqrt(0.1 * self.strength * self.active)
        while self.active and self.cooldown < 0.0:
            self.cooldown += math.sqrt(10 / (self.strength * self.active))
            Particle(
                init_pos=self.owner.pos
                + Vector3(
                    *internal_coord_to_xy(
                        self.pos.xy
                        + Vector2(random.uniform(-WIDTH, WIDTH), 0).rotate(self.pos.z),
                        self.owner.pos.z,
                    ),
                    0.0,
                ),
                init_speed=self.owner.speed
                + Vector3(
                    *internal_coord_to_xy(
                        Vector2(0.0, PARTICLE_SPEED).rotate(
                            self.pos.z + random.uniform(-ANGLE_SPREAD, ANGLE_SPREAD),
                        ),
                        self.owner.pos.z,
                    ),
                    0.0,
                ),
                ttl=random.uniform(100, 200),
            )
