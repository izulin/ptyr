from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame as pg
from pygame import Vector3

from assets import PlayerImages
from config import CONFIG
from consts import CYAN, GREEN
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS
from delayed import DelayedEvent
from engines import Engine
from explosions import LargeExplosion, explosion_effect
from gamepad import get_gamepad
from groups import (
    ALL_PLAYERS,
    try_and_spawn_object,
)
from objects import (
    Collides,
    DrawsUI,
    HasEngines,
    HasHitpoints,
    HasMass,
    HasShield,
    Moves,
    Object,
    StaticDrawable,
)
from postprocessing import with_outline
from weapons import SingleShotWeapon, SmallMissileWeapon, Weapon

if TYPE_CHECKING:
    from pygame._sdl2.controller import Controller


class Player(
    HasShield,
    HasHitpoints,
    HasMass,
    DrawsUI,
    HasEngines,
    Collides,
    StaticDrawable,
    Moves,
    Object,
):
    DRAG = 1 / 1000
    ANGULAR_DRAG = 2 / 1000

    MASS = 30.0
    HP = 30.0
    SHIELD = 30.0

    controls: dict[str, int]
    weapon: Weapon | None
    secondary_weapon: Weapon | None
    player_id: int

    def __init__(
        self,
        *args,
        controls: dict[str, int],
        player_id: int,
        color: pg.Color,
        gamepad: Controller,
        **kwargs,
    ):
        super().__init__(ALL_PLAYERS, *args, **kwargs)
        self.color = color
        self.controls = controls
        self.gamepad = gamepad
        self.weapon = None
        self.secondary_weapon = None
        self.use_defaults()
        self.player_id = player_id
        self.back_engine = Engine(
            pos=Vector3(0, -10, 180),
            strength=1,
            owner=self.owner,
        )
        self.back_left_engine = Engine(
            pos=Vector3(-5, -9, 90 + 45),
            strength=1 / 3,
            owner=self.owner,
        )
        self.back_right_engine = Engine(
            pos=Vector3(5, -9, 270 - 45),
            strength=1 / 3,
            owner=self.owner,
        )
        self.front_left_engine = Engine(
            pos=Vector3(-2, 9, 90 - 45),
            strength=1 / 3,
            owner=self.owner,
        )
        self.front_right_engine = Engine(
            pos=Vector3(2, 9, 270 + 45),
            strength=1 / 3,
            owner=self.owner,
        )

    def use_defaults(self):
        if self.weapon is None:
            self.default_weapon()
        if self.secondary_weapon is None:
            self.default_secondary_weapon()

    def default_weapon(self):
        SingleShotWeapon(owner=self.owner)
        # LaserWeapon(owner=self.owner)

    def default_secondary_weapon(self):
        SmallMissileWeapon(owner=self.owner)
        pass

    def with_postprocessing(self):
        return with_outline(self, self.color)

    def update(self, dt: float):
        self.use_defaults()
        pressed_keys = pg.key.get_pressed()
        if (
            pressed_keys[self.controls["shoot"]]
            or self.gamepad.get_button(
                pg.CONTROLLER_BUTTON_B,
            )
        ) and self.weapon is not None:
            self.weapon.fire()
        if (
            pressed_keys[self.controls["secondary"]]
            or self.gamepad.get_button(
                pg.CONTROLLER_BUTTON_A,
            )
        ) and self.secondary_weapon is not None:
            self.secondary_weapon.fire()

        left_right_axis = self.gamepad.get_axis(0) / 2**15
        forward_backward_axis = self.gamepad.get_axis(1) / 2**15
        left_dir = max(-left_right_axis, 0.0)
        if pressed_keys[self.controls["left_turn"]]:
            left_dir += 1.0
        if left_dir < 0.25:
            left_dir = 0.0
        right_dir = max(left_right_axis, 0.0)
        if pressed_keys[self.controls["right_turn"]]:
            right_dir += 1.0
        if right_dir < 0.25:
            right_dir = 0.0
        forward_dir = max(-forward_backward_axis, 0.0)
        if pressed_keys[self.controls["forward"]]:
            forward_dir += 1.0
        if forward_dir < 0.25:
            forward_dir = 0.0
        backward_dir = max(forward_backward_axis, 0.0)
        if pressed_keys[self.controls["backward"]]:
            backward_dir += 1.0
        if backward_dir < 0.25:
            backward_dir = 0.0

        for engine in self.all_engines:
            engine.active = 0
        self.back_engine.active += forward_dir
        self.back_right_engine.active += forward_dir
        self.back_left_engine.active += forward_dir
        self.front_right_engine.active += backward_dir
        self.front_left_engine.active += backward_dir
        if pressed_keys[self.controls["right_strafe"]] or self.gamepad.get_button(
            pg.CONTROLLER_BUTTON_RIGHTSHOULDER,
        ):
            self.back_left_engine.active += 1
            self.front_left_engine.active += 1
        if pressed_keys[self.controls["left_strafe"]] or self.gamepad.get_button(
            pg.CONTROLLER_BUTTON_LEFTSHOULDER,
        ):
            self.back_right_engine.active += 1
            self.front_right_engine.active += 1
        self.back_left_engine.active += left_dir
        self.front_right_engine.active += left_dir

        self.back_right_engine.active += right_dir
        self.front_left_engine.active += right_dir
        super().update(dt)

    def on_death(self):
        DelayedEvent(
            lambda: spawn_player(self.player_id),
            2000,
            repeat=False,
            name=f"spawn_player {self.player_id}",
        )
        LargeExplosion(init_pos=self.pos, init_speed=self.speed, owner=self.owner)
        explosion_effect(owner=self)
        super().on_death()


def spawn_player(player_id):
    # assert get_player(player_id) is None
    assert player_id in [1, 2]
    controls = {1: PLAYER_1_CONTROLS, 2: PLAYER_2_CONTROLS}[player_id]
    image = {1: PlayerImages[2], 2: PlayerImages[1]}[player_id]
    color = {1: GREEN, 2: CYAN}[player_id]

    spawned_players = try_and_spawn_object(
        lambda: Player(
            controls=controls,
            gamepad=get_gamepad(player_id),
            image=image,
            init_pos=(
                random.randint(0, CONFIG.SCREEN_WIDTH),
                random.randint(0, CONFIG.SCREEN_HEIGHT),
                random.randint(0, 360),
            ),
            init_speed=(0, 0, 0),
            player_id=player_id,
            color=color,
        ),
        1,
        1000,
    )
    if not spawned_players:
        print(f"Unable to spawn player {player_id}.")
        raise RuntimeError


def get_player(player_id) -> Player | None:
    player: Player
    for player in ALL_PLAYERS.sprites():
        if player.player_id == player_id:
            return player
    return None
