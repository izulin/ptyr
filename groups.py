from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enemies import Asteroid
    from objects import MovingObject
    from players import Player

ALL_ASTEROIDS: pygame.sprite.Group[Asteroid] = pygame.sprite.Group()
ALL_PLAYERS: pygame.sprite.Group[Player] = pygame.sprite.Group()
ALL_SPRITES: pygame.sprite.Group[MovingObject] = pygame.sprite.Group()
