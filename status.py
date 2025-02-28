from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING

from assets import HealPowerupImage
from groups import ALL_WITH_UPDATE

if TYPE_CHECKING:
    from objects import Object, HasHitpoints


class Status(pg.sprite.Sprite):
    TTL = None
    owner: Object

    def __init__(self, *args, owner: Object, ttl=None, **kwargs):
        super().__init__(ALL_WITH_UPDATE, owner.all_statuses, *args, **kwargs)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for status in self.owner.all_statuses:
            if isinstance(status, HealingStatus) and status != self:
                self.ttl += status.ttl
                status.kill()

    def update(self, dt: float):
        self.owner.heal_hp(self.HEAL_AMOUNT * dt / self.ttl)
        super().update(dt)
