from __future__ import annotations

from pygame import Vector2, Vector3

from assets import AsteroidLargeImages, AsteroidMediumImages, AsteroidSmallImages
from consts import SCREEN_WIDTH, SCREEN_HEIGHT
from groups import ALL_ASTEROIDS, ALL_COLLIDING_OBJECTS, ALL_DRAWABLE_OBJECTS
from objects import StaticObject, HasHitpoints
import random

from powerups import get_random_powerup


class Asteroid(HasHitpoints, StaticObject):
    GROUPS = (
        ALL_COLLIDING_OBJECTS,
        ALL_DRAWABLE_OBJECTS,
        ALL_ASTEROIDS,
    )


class LargeAsteroid(Asteroid):
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


class MediumAsteroid(Asteroid):
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


class SmallAsteroid(Asteroid):
    MASS = 10.0
    HP = 10.0
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
        if ALL_COLLIDING_OBJECTS.cd.collide_with_callback(asteroid, stationary=True):
            asteroid.kill()
        else:
            return
    print("Unable to spawn asteroid.")
