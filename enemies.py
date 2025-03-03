from __future__ import annotations

import random

from pygame import Vector2, Vector3

from assets import (
    AsteroidLargeImages,
    AsteroidMediumImages,
    AsteroidSmallImages,
    GeometricEnemyAnimation,
)
from config import CONFIG
from consts import RED
from explosions import SmallExplosion
from groups import ALL_ENEMIES, try_and_spawn_object
from objects import (
    AnimatedDrawable,
    Collides,
    DrawsUI,
    HasHitpoints,
    HasMass,
    HasShield,
    Object,
    StaticDrawable,
    UsesPhysics,
)
from postprocessing import with_outline
from powerups import get_random_powerup


class GeometricEnemy(
    AnimatedDrawable,
    UsesPhysics,
    HasShield,
    HasHitpoints,
    HasMass,
    DrawsUI,
    Collides,
    Object,
):
    DRAG = 1 / 1000
    ANGULAR_DRAG = 2 / 1000

    MASS = 30.0
    HP = 30.0
    SHIELD = 30.0

    IMAGE = GeometricEnemyAnimation

    def __init__(self, *args, **kwargs):
        super().__init__(ALL_ENEMIES, *args, **kwargs)
        self.color = RED

    def with_postprocessing(self):
        return with_outline(self, self.color)


class Asteroid(UsesPhysics, HasHitpoints, HasMass, DrawsUI, Collides, Object):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(ALL_ENEMIES, *args, **kwargs)
        self.color = RED

    def with_postprocessing(self):
        return with_outline(self, self.color)


class LargeAsteroid(StaticDrawable, Asteroid):
    MASS = 100.0
    HP = 100.0
    IMAGE = AsteroidLargeImages

    def on_death(self):
        def _tmp():
            ang = random.uniform(0, 360)
            return MediumAsteroid(
                init_pos=self.pos
                + Vector3(
                    *Vector2(random.uniform(10.0, 40.0), 0.0).rotate(ang),
                    random.randint(0, 360),
                ),
                init_speed=self.speed
                + Vector3(*Vector2(0.05, 0.0).rotate(ang), random.uniform(-0.1, 0.1)),
            )

        try_and_spawn_object(_tmp, 3, 20)
        get_random_powerup()(init_pos=Vector3(*self.pos_xy, 0))
        super().on_death()


class MediumAsteroid(StaticDrawable, Asteroid):
    MASS = 30.0
    HP = 30.0
    IMAGE = AsteroidMediumImages

    def on_death(self):
        def _tmp():
            ang = random.uniform(0, 360)
            return SmallAsteroid(
                init_pos=self.pos
                + Vector3(
                    *Vector2(random.uniform(5.0, 20.0), 0.0).rotate(ang),
                    random.randint(0, 360),
                ),
                init_speed=self.speed
                + Vector3(*Vector2(0.05, 0.0).rotate(ang), random.uniform(-0.1, 0.1)),
            )

        try_and_spawn_object(_tmp, 3, 20)
        super().on_death()


class SmallAsteroid(StaticDrawable, Asteroid):
    MASS = 10.0
    HP = 10.0
    IMAGE = AsteroidSmallImages

    def on_death(self):
        SmallExplosion(init_pos=self.pos, init_speed=self.speed, owner=self.owner)
        super().on_death()


def spawn_random_enemy():
    random.choice([spawn_geometric_enemy, spawn_asteroid])()


def spawn_geometric_enemy():
    succ = try_and_spawn_object(
        lambda: GeometricEnemy(
            init_pos=[
                random.randint(0, CONFIG.SCREEN_WIDTH),
                random.randint(0, CONFIG.SCREEN_HEIGHT),
                random.randint(0, 360),
            ],
            init_speed=[
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
                0.0,
            ],
        ),
        1,
        10,
    )
    if not succ:
        print("Unable to spawn enemy.")


def spawn_asteroid():
    succ = try_and_spawn_object(
        lambda: LargeAsteroid(
            init_pos=[
                random.randint(0, CONFIG.SCREEN_WIDTH),
                random.randint(0, CONFIG.SCREEN_HEIGHT),
                random.randint(0, 360),
            ],
            init_speed=[
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
            ],
        ),
        1,
        10,
    )
    if not succ:
        print("Unable to spawn asteroid.")
