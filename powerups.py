from __future__ import annotations
from assets import HealPowerupImage
from delayed import DelayedEvent
from groups import ALL_POWERUPS, ALL_DRAWABLE_OBJECTS
from objects import StaticObject, MovingObject, HasTimer
import random


class PowerUp(HasTimer, StaticObject):
    DRAG = 100 / 1000
    ANGULAR_DRAG = 200 / 1000
    GROUPS = (
        ALL_DRAWABLE_OBJECTS,
        ALL_POWERUPS,
    )
    TTL = 10_000

    used: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.used = False

    def on_collision(self, other: MovingObject):
        if self.used:
            return

        if not isinstance(other, StaticObject):
            self.used = True
            self.on_player_action(other)
            DelayedEvent(lambda: self.mark_dead(), 100, name="Powerup cleanup")

    def on_player_action(self, other: MovingObject):
        raise NotImplemented


class HealPowerUp(PowerUp):
    IMAGE = HealPowerupImage

    def on_player_action(self, other: MovingObject):
        other.heal_hp(50.0)


def get_random_powerup() -> type[PowerUp]:
    return random.choice([HealPowerUp])
