from __future__ import annotations
from assets import (
    HealPowerupImage,
    DoubleShotWeaponImage,
    MineLauncherWeaponImage,
    MissileLauncherWeaponImage,
)
from consts import YELLOW
from delayed import DelayedEvent
from postprocessing import with_outline
from status import HealingStatus
from groups import ALL_POWERUPS
from objects import MovingObject, HasTimer, StaticDrawable
import random
from players import Player
from weapons import DoubleShotWeapon, MineLauncher, SmallMissileWeapon


class PowerUp(HasTimer, MovingObject):
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    TTL = 30_000

    used: bool

    def __init__(self, *args, **kwargs):
        self._layer = -1
        super().__init__(ALL_POWERUPS, *args, **kwargs)
        self.used = False

    def with_postprocessing(self):
        return with_outline(self, YELLOW)

    def on_collision(self, other: MovingObject):
        if self.used:
            return

        if isinstance(other, Player):
            self.used = True
            self.action_logic(other)
            DelayedEvent(lambda: self.mark_dead(), 100, name="Powerup cleanup")

    def action_logic(self, other: Player):
        raise NotImplementedError


class HealPowerUp(StaticDrawable, PowerUp):
    IMAGE = HealPowerupImage

    def action_logic(self, other: Player):
        HealingStatus(owner=other)
        HealingStatus(owner=other)


class DoubleShotWeaponPowerUp(StaticDrawable, PowerUp):
    IMAGE = DoubleShotWeaponImage

    def action_logic(self, other: Player):
        DoubleShotWeapon(owner=other)


class MineLauncherWeaponPowerUp(StaticDrawable, PowerUp):
    IMAGE = MineLauncherWeaponImage

    def action_logic(self, other: Player):
        MineLauncher(owner=other)


class MissileLauncherWeaponPowerUp(StaticDrawable, PowerUp):
    IMAGE = MissileLauncherWeaponImage

    def action_logic(self, other: Player):
        SmallMissileWeapon(owner=other)


def get_random_powerup() -> type[PowerUp]:
    return random.choice(
        [
            HealPowerUp,
            DoubleShotWeaponPowerUp,
            MineLauncherWeaponPowerUp,
            MissileLauncherWeaponPowerUp,
        ]
    )
