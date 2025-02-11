from __future__ import annotations

from pygame import Vector2, Vector3

from assets import AsteroidLargeImages, AsteroidMediumImages, AsteroidSmallImages
from collisions import COLLIDING_SPRITES_CD
from consts import SCREEN_WIDTH, SCREEN_HEIGHT
from groups import ALL_ASTEROIDS
from objects import StaticObject, HasHitpoints
import random

from powerups import get_powerup


class LargeAsteroid(HasHitpoints, StaticObject):
    MASS = 100.0
    HP = 100.0
    GROUPS = StaticObject.GROUPS + (ALL_ASTEROIDS,)
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
        get_powerup()(init_pos=self.pos, init_speed=self.speed)


class MediumAsteroid(HasHitpoints, StaticObject):
    MASS = 30.0
    HP = 30.0
    GROUPS = StaticObject.GROUPS + (ALL_ASTEROIDS,)
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


class SmallAsteroid(HasHitpoints, StaticObject):
    MASS = 10.0
    HP = 10.0
    GROUPS = StaticObject.GROUPS + (ALL_ASTEROIDS,)
    IMAGE = AsteroidSmallImages


def spawn_asteroid():
    for reps in range(100):
        asteroid = LargeAsteroid(
            init_pos=[
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.randint(0, 360),
            ],
            init_speed=[
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1),
            ],
        )
        if COLLIDING_SPRITES_CD.collide_with_callback(asteroid, stationary=True):
            asteroid.kill()
        else:
            return
    print("Unable to spawn asteroid.")
