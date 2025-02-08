from __future__ import annotations

import random

import pygame
from pygame import Vector2

from assets import PlayerImages
from collisions import ALL_SPRITES_CD
from consts import SCREEN_WIDTH, SCREEN_HEIGHT
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS
from groups import ALL_PLAYERS
from objects import MovingObject
from weapons import BasicWeapon, SinglePlasma


class Player(MovingObject):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = 0.05 / 1000
    ANGULAR_THRUST = 0.2 / 1000

    MASS = 30.0

    controls: dict[str, int]
    weapon: BasicWeapon

    def __init__(self, *args, controls, **kwargs):
        super().__init__(*args, **kwargs)
        self.controls = controls
        self.add(ALL_PLAYERS)
        self.weapon = self.default_weapon()

    def default_weapon(self):
        return SinglePlasma(owner=self, cooldown=10, ammo=None)

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


def spawn_player(player_num):
    assert player_num in [1, 2]
    for _ in range(1000):
        controls = {1: PLAYER_1_CONTROLS, 2: PLAYER_2_CONTROLS}[player_num]
        image = {1: PlayerImages[2], 2: PlayerImages[1]}[player_num]

        player = Player(
            controls=controls,
            image=image,
            init_pos=(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.randint(0, 360),
            ),
            init_speed=(0, 0, 0),
        )

        if ALL_SPRITES_CD.collide_with_callback(player, stationary=True):
            player.kill()
        else:
            return
    print(f"Unable to spawn player {player_num}.")
    raise RuntimeError
