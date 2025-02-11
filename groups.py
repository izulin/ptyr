from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enemies import LargeAsteroid
    from objects import MovingObject
    from players import Player
    from powerups import PowerUp

ALL_ASTEROIDS: pg.sprite.Group[LargeAsteroid] = pg.sprite.Group()
ALL_PLAYERS: pg.sprite.Group[Player] = pg.sprite.Group()
ALL_SPRITES: pg.sprite.Group[MovingObject] = pg.sprite.Group()
ALL_POWERUPS: pg.sprite.Group[PowerUp] = pg.sprite.Group()
