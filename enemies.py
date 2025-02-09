from __future__ import annotations

from assets import AsteroidLargeImage, ExplosionImage
from collisions import ALL_SPRITES_CD
from consts import SCREEN_WIDTH, SCREEN_HEIGHT
from groups import ALL_ASTEROIDS
from objects import PassiveObject
import random


class Asteroid(PassiveObject):
    MASS = 100.0
    HP = 100.0
    IMAGE = AsteroidLargeImage

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(ALL_ASTEROIDS)


def spawn_asteroid():
    for reps in range(100):
        asteroid = Asteroid(
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
        if ALL_SPRITES_CD.collide_with_callback(asteroid, stationary=True):
            asteroid.kill()
        else:
            return
    print("Unable to spawn asteroid.")
