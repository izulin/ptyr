from __future__ import annotations

import random

import pygame as pg
from pygame import Vector2, Vector3


from assets import PlayerImages
from consts import SCREEN_WIDTH, SCREEN_HEIGHT
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS
from delayed import DelayedEvent
from explosions import LargeExplosion
from groups import (
    ALL_PLAYERS,
    ALL_COLLIDING_OBJECTS,
    ALL_DRAWABLE_OBJECTS,
)
from math_utils import internal_coord_to_xy
from objects import (
    MovingObject,
    HasShield,
    HasHitpoints,
    Collides,
    StaticDrawable,
    DrawsUI,
)
from particles import Particle
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
        self.owner = self
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
        SingleShotWeapon(owner=self.owner)

    def default_secondary_weapon(self):
        MineLauncher(owner=self.owner)
        pass

    def get_accels(self) -> tuple[Vector2, float]:
        forward_accel = self.FORWARD_THRUST * (
            self.engine_to_forward - self.engine_to_backward
        )
        angular_accel = self.ANGULAR_THRUST * (
            self.engine_turn_left - self.engine_turn_right
        )
        side_accel = self.SIDE_THRUST * (self.engine_to_right - self.engine_to_left)

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
        self.engine_to_forward = int(pressed_keys[self.controls["forward"]])
        self.engine_to_backward = int(pressed_keys[self.controls["backward"]])
        self.engine_to_left = int(pressed_keys[self.controls["left_strafe"]])
        self.engine_to_right = int(pressed_keys[self.controls["right_strafe"]])
        self.engine_turn_left = int(pressed_keys[self.controls["left_turn"]])
        self.engine_turn_right = int(pressed_keys[self.controls["right_turn"]])
        if self.engine_to_forward:
            Particle(
                init_pos=self.pos
                + Vector3(
                    *internal_coord_to_xy(
                        Vector2(0.0, -10.0).rotate(random.uniform(-10, 10)), self.pos.z
                    ),
                    0.0,
                ),
                init_speed=self.speed
                + Vector3(
                    *internal_coord_to_xy(
                        Vector2(0.0, -0.1).rotate(random.uniform(-10, 10)), self.pos.z
                    ),
                    0.0,
                ),
                ttl=random.uniform(100, 200),
            )
        super().update(dt)

    def on_death(self):
        DelayedEvent(
            lambda: spawn_player(self.player_id),
            2000,
            repeat=False,
            name=f"spawn_player {self.player_id}",
        )
        LargeExplosion(init_pos=self.pos, init_speed=self.speed, owner=self.owner)
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
