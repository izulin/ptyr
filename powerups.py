from __future__ import annotations

import random

from assets import (
    DoubleShotWeaponImage,
    HealPowerupImage,
    LaserWeaponImage,
    MineLauncherWeaponImage,
    MissileLauncherWeaponImage,
)
from consts import YELLOW
from delayed import DelayedEvent
from groups import ALL_POWERUPS
from objects import HasTimer, Object, StaticDrawable, Stationary
from players import Player
from postprocessing import with_outline
from status import HealingStatus
from weapons import DoubleShotWeapon, LaserWeapon, MineLauncher, SmallMissileWeapon


class PowerUp(StaticDrawable, Stationary, HasTimer, Object):
    TTL = 30_000

    used: bool

    def __init__(self, *args, **kwargs):
        self._layer = -1
        super().__init__(ALL_POWERUPS, *args, **kwargs)
        self.used = False

    def with_postprocessing(self):
        return with_outline(self, YELLOW)

    def on_collision(self, other: Object):
        if self.used:
            return

        if isinstance(other, Player):
            self.used = True
            self.action_logic(other)
            DelayedEvent(lambda: self.mark_dead(), 100, name="Powerup cleanup")

    def action_logic(self, other: Player):
        raise NotImplementedError


class HealPowerUp(PowerUp):
    IMAGE = HealPowerupImage

    def action_logic(self, other: Player):
        HealingStatus(owner=other)
        HealingStatus(owner=other)


class DoubleShotWeaponPowerUp(PowerUp):
    IMAGE = DoubleShotWeaponImage

    def action_logic(self, other: Player):
        DoubleShotWeapon(owner=other)


class MineLauncherWeaponPowerUp(PowerUp):
    IMAGE = MineLauncherWeaponImage

    def action_logic(self, other: Player):
        MineLauncher(owner=other)


class MissileLauncherWeaponPowerUp(PowerUp):
    IMAGE = MissileLauncherWeaponImage

    def action_logic(self, other: Player):
        SmallMissileWeapon(owner=other)


class LaserWeaponPowerUp(PowerUp):
    IMAGE = LaserWeaponImage

    def action_logic(self, other: Player):
        LaserWeapon(owner=other)


def get_random_powerup() -> type[PowerUp]:
    return random.choice(
        [
            HealPowerUp,
            DoubleShotWeaponPowerUp,
            MineLauncherWeaponPowerUp,
            MissileLauncherWeaponPowerUp,
            LaserWeaponPowerUp,
        ],
    )
