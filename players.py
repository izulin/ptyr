from __future__ import annotations

import random

import pygame as pg
from pygame import Vector3


from assets import PlayerImages
from consts import SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, CYAN
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS
from delayed import DelayedEvent
from engines import Engine
from explosions import LargeExplosion, explosion_effect
from groups import (
    ALL_PLAYERS,
    try_and_spawn_object,
)
from objects import (
    Object,
    HasShield,
    HasHitpoints,
    Collides,
    StaticDrawable,
    DrawsUI,
    HasEngines,
    UsesPhysics,
    HasMass,
)
from postprocessing import with_outline
from weapons import Weapon, SingleShotWeapon, SmallMissileWeapon, LaserWeapon


class Player(
    StaticDrawable,
    HasShield,
    HasHitpoints,
    HasMass,
    DrawsUI,
    HasEngines,
    Collides,
    UsesPhysics,
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
        self, *args, controls: dict[str, int], player_id: int, color: pg.Color, **kwargs
    ):
        super().__init__(ALL_PLAYERS, *args, **kwargs)
        self.color = color
        self.controls = controls
        self.weapon = None
        self.secondary_weapon = None
        self.use_defaults()
        self.player_id = player_id
        self.back_engine = Engine(
            pos=Vector3(0, -10, 180), strength=1, owner=self.owner
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
        #SingleShotWeapon(owner=self.owner)
        LaserWeapon(owner=self.owner)

    def default_secondary_weapon(self):
        SmallMissileWeapon(owner=self.owner)
        pass

    def with_postprocessing(self):
        return with_outline(self, self.color)

    def update(self, dt: float):
        self.use_defaults()
        pressed_keys = pg.key.get_pressed()
        if pressed_keys[self.controls["shoot"]]:
            if self.weapon is not None:
                self.weapon.fire()
        if pressed_keys[self.controls["secondary"]]:
            if self.secondary_weapon is not None:
                self.secondary_weapon.fire()
        for engine in self.all_engines:
            engine.active = 0
        if pressed_keys[self.controls["forward"]]:
            self.back_engine.active += 1
            self.back_right_engine.active += 1
            self.back_left_engine.active += 1
        if pressed_keys[self.controls["backward"]]:
            self.front_right_engine.active += 1
            self.front_left_engine.active += 1
        if pressed_keys[self.controls["right_strafe"]]:
            self.back_left_engine.active += 1
            self.front_left_engine.active += 1
        if pressed_keys[self.controls["left_strafe"]]:
            self.back_right_engine.active += 1
            self.front_right_engine.active += 1
        if pressed_keys[self.controls["left_turn"]]:
            self.back_left_engine.active += 1
            self.front_right_engine.active += 1
        if pressed_keys[self.controls["right_turn"]]:
            self.back_right_engine.active += 1
            self.front_left_engine.active += 1
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
    assert get_player(player_id) is None
    assert player_id in [1, 2]
    controls = {1: PLAYER_1_CONTROLS, 2: PLAYER_2_CONTROLS}[player_id]
    image = {1: PlayerImages[2], 2: PlayerImages[1]}[player_id]
    color = {1: GREEN, 2: CYAN}[player_id]
    spawned_players = try_and_spawn_object(
        lambda: Player(
            controls=controls,
            image=image,
            init_pos=(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
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
