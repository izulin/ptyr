from __future__ import annotations
import pygame
from pygame import Vector2

from groups import ALL_PLAYERS
from objects import MovingObject
from weapons import Weapon


class Player(MovingObject):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = 0.05 / 1000
    ANGULAR_THRUST = 0.2 / 1000

    MASS = 30.0

    controls: dict[str, int]
    weapon: Weapon

    def __init__(self, *args, controls, **kwargs):
        super().__init__(*args, **kwargs)
        self.controls = controls
        self.add(ALL_PLAYERS)
        self.weapon = self.default_weapon()

    def default_weapon(self):
        return Weapon(owner=self, cooldown=10, ammo=None)

    def get_accels(self) -> tuple[Vector2, float]:
        pressed_keys = pygame.key.get_pressed()

        forward_accel = self.FORWARD_THRUST * (
            int(pressed_keys[self.controls["forward"]])
            - int(pressed_keys[self.controls["backward"]])
        )
        angular_accel = self.ANGULAR_THRUST * (
            int(pressed_keys[self.controls["left_turn"]])
            - int(pressed_keys[self.controls["right_turn"]])
        )
        side_accel = self.SIDE_THRUST * (
            int(pressed_keys[self.controls["right_strafe"]])
            - int(pressed_keys[self.controls["left_strafe"]])
        )

        return Vector2(side_accel, forward_accel), angular_accel

    def update(self, dt: float):
        pressed_keys = pygame.key.get_pressed()
        self.weapon.update(dt)
        if pressed_keys[self.controls["shoot"]]:
            self.weapon.fire()
        super().update(dt)
