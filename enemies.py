from __future__ import annotations

from pygame import Vector2, Vector3

from assets import AsteroidLargeImages, AsteroidMediumImages, AsteroidSmallImages
from consts import SCREEN_WIDTH, SCREEN_HEIGHT
from explosions import SmallExplosion
from groups import ALL_ENEMIES, ALL_COLLIDING_OBJECTS
from objects import (
    NoControl,
    HasHitpoints,
    Collides,
    StaticDrawable,
    MovingObject,
    DrawsUI,
)
import random

from powerups import get_random_powerup


class Asteroid(Collides, HasHitpoints, NoControl, DrawsUI, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(ALL_ENEMIES, *args, **kwargs)


class LargeAsteroid(StaticDrawable, Asteroid):
    MASS = 100.0
    HP = 100.0
    IMAGE = AsteroidLargeImages

    def on_death(self):
        shift_pos = Vector2(12.0, 0.0)
        shift_speed = Vector2(0.1, 0.0)
        for i in range(3):
            MediumAsteroid(
                init_pos=self.pos
                + Vector3(*shift_pos.rotate(120 * i), random.randint(0, 360)),
                init_speed=self.speed
                + Vector3(*shift_speed.rotate(120 * i), random.uniform(-0.1, 0.1)),
            )
        get_random_powerup()(init_pos=self.pos, init_speed=self.speed)
        super().on_death()


class MediumAsteroid(StaticDrawable, Asteroid):
    MASS = 30.0
    HP = 30.0
    IMAGE = AsteroidMediumImages

    def on_death(self):
        shift_pos = Vector2(12.0, 0.0)
        shift_speed = Vector2(0.1, 0.0)
        for i in range(3):
            SmallAsteroid(
                init_pos=self.pos
                + Vector3(*shift_pos.rotate(120 * i), random.randint(0, 360)),
                init_speed=self.speed
                + Vector3(*shift_speed.rotate(120 * i), random.uniform(-0.1, 0.1)),
            )
        super().on_death()


class SmallAsteroid(StaticDrawable, Asteroid):
    MASS = 10.0
    HP = 10.0
    IMAGE = AsteroidSmallImages

    def on_death(self):
        SmallExplosion(init_pos=self.pos, init_speed=self.speed)
        super().on_death()


def spawn_asteroid():
    for reps in range(100):
        asteroid = LargeAsteroid(
            init_pos=[
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.randint(0, 360),
            ],
            init_speed=[
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
            ],
        )
        if ALL_COLLIDING_OBJECTS.cd.collide_with_callback(asteroid):
            asteroid.kill()
        else:
            return
    print("Unable to spawn asteroid.")
