from __future__ import annotations
from assets import HealPowerupImage, DoubleShotWeaponImage, MineLauncherWeaponImage
from delayed import DelayedEvent
from status import HealingStatus
from groups import ALL_POWERUPS
from objects import NoControl, MovingObject, HasTimer, StaticDrawable
import random
from typing import TYPE_CHECKING

from weapons import DoubleShotWeapon, MineLauncher

if TYPE_CHECKING:
    from players import Player


class PowerUp(HasTimer, NoControl, MovingObject):
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    TTL = 10_000

    used: bool

    def __init__(self, *args, **kwargs):
        super().__init__(ALL_POWERUPS, *args, **kwargs)
        self.used = False

    def on_player_action(self, other: MovingObject):
        if self.used:
            return

        if not isinstance(other, NoControl):
            self.used = True
            self.action_logic(other)
            DelayedEvent(lambda: self.mark_dead(), 100, name="Powerup cleanup")

    def action_logic(self, other: Player):
        raise NotImplemented


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


def get_random_powerup() -> type[PowerUp]:
    return random.choice(
        [HealPowerUp, DoubleShotWeaponPowerUp, MineLauncherWeaponPowerUp]
    )
