from __future__ import annotations
from assets import (
    HealPowerupImage,
    DoubleShotWeaponImage,
    MineLauncherWeaponImage,
    MissileLauncherWeaponImage,
    LaserWeaponImage,
)
from consts import YELLOW
from delayed import DelayedEvent
from postprocessing import with_outline
from status import HealingStatus
from groups import ALL_POWERUPS
from objects import Object, HasTimer, StaticDrawable
import random
from players import Player
from weapons import DoubleShotWeapon, MineLauncher, SmallMissileWeapon, LaserWeapon


class PowerUp(StaticDrawable, HasTimer, Object):
    # DRAG = 100 / 1000
    # ANGULAR_DRAG = 200 / 1000
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
        ]
    )
