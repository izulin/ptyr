from __future__ import annotations
from assets import HealPowerUpImage
from delayed import DelayedEvent
from objects import PassiveObject, MovingObject
import random


class PowerUp(PassiveObject):
    DMG = 1000.0
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    MASS = None
    COLLIDES = False
    IMAGE = HealPowerUpImage

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.used = False

    def on_collision(self, other: MovingObject):
        if self.used:
            return
        from players import Player

        if isinstance(other, Player):
            self.used = True
            other.heal_hp(50.0)
            DelayedEvent(lambda: self.make_dead(), 100, name="Powerup cleanup")


ALL_POWERUPS = [PowerUp]


def get_powerup() -> type[PowerUp]:
    return random.choice(ALL_POWERUPS)
