from __future__ import annotations

import random

import pygame as pg
from pygame.math import Vector2

from assets import PlayerImages
from consts import SCREEN_WIDTH, SCREEN_HEIGHT
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS
from delayed import DelayedEvent
from explosions import LargeExplosion
from groups import (
    ALL_PLAYERS,
    ALL_COLLIDING_OBJECTS,
)
from objects import (
    MovingObject,
    HasShield,
    HasHitpoints,
    Collides,
    StaticDrawable,
    DrawsUI,
)
from weapons import Weapon, SingleShotWeapon, MineLauncher


class Player(StaticDrawable, Collides, HasShield, HasHitpoints, DrawsUI, MovingObject):
    DRAG = 1 / 1000
    ANGULAR_DRAG = 2 / 1000

    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = 0.05 / 1000
    ANGULAR_THRUST = 0.2 / 1000

    MASS = 30.0
    HP = 30.0
    SHIELD = 30.0

    controls: dict[str, int]
    weapon: Weapon | None
    secondary_weapon: Weapon | None
    player_id: int

    def __init__(self, *args, controls: dict[str, int], player_id: int, **kwargs):
        super().__init__(ALL_PLAYERS, *args, **kwargs)
        self.controls = controls
        self.weapon = None
        self.secondary_weapon = None
        self.use_defaults()
        self.player_id = player_id

    def use_defaults(self):
        if self.weapon is None:
            self.default_weapon()
        if self.secondary_weapon is None:
            self.default_secondary_weapon()

    def default_weapon(self):
        SingleShotWeapon(owner=self)

    def default_secondary_weapon(self):
        MineLauncher(owner=self)
        pass

    def get_accels(self) -> tuple[Vector2, float]:
        pressed_keys = pg.key.get_pressed()

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
        self.use_defaults()
        pressed_keys = pg.key.get_pressed()
        if pressed_keys[self.controls["shoot"]]:
            if self.weapon is not None:
                self.weapon.fire()
        if pressed_keys[self.controls["secondary"]]:
            if self.secondary_weapon is not None:
                self.secondary_weapon.fire()
        super().update(dt)

    def on_death(self):
        DelayedEvent(
            lambda: spawn_player(self.player_id),
            2000,
            repeat=False,
            name=f"spawn_player {self.player_id}",
        )
        LargeExplosion(init_pos=self.pos, init_speed=self.speed)
        super().on_death()


def spawn_player(player_id):
    assert get_player(player_id) is None
    assert player_id in [1, 2]
    for _ in range(1000):
        controls = {1: PLAYER_1_CONTROLS, 2: PLAYER_2_CONTROLS}[player_id]
        image = {1: PlayerImages[2], 2: PlayerImages[1]}[player_id]

        player = Player(
            controls=controls,
            image=image,
            init_pos=(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.randint(0, 360),
            ),
            init_speed=(0, 0, 0),
            player_id=player_id,
        )

        if ALL_COLLIDING_OBJECTS.cd.collide_with_callback(player):
            player.kill()
        else:
            return
    print(f"Unable to spawn player {player_id}.")
    raise RuntimeError


def get_player(player_id) -> Player | None:
    player: Player
    for player in ALL_PLAYERS.sprites():
        if player.player_id == player_id:
            return player
    return None
