from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING

from assets import HealPowerupImage
from groups import ALL_STATUSES

if TYPE_CHECKING:
    from objects import MovingObject, HasHitpoints


class Status(pg.sprite.Sprite):
    TTL = None
    owner: MovingObject

    def __init__(self, *args, owner: MovingObject, ttl=None, **kwargs):
        super().__init__(ALL_STATUSES, owner.all_statuses, *args, **kwargs)
        if ttl is None:
            ttl = self.TTL
        self.ttl = ttl
        self.owner = owner

    def update(self, dt: float):
        if self.ttl is not None:
            self.ttl -= dt
            if self.ttl <= 0:
                self.kill()


class HealingStatus(Status):
    TTL = 5_000
    HEAL_AMOUNT = 50
    owner: HasHitpoints
    icon = HealPowerupImage.scale((10, 10))

    def update(self, dt: float):
        self.owner.heal_hp(self.HEAL_AMOUNT * dt / self.ttl)
        super().update(dt)
