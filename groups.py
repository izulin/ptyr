from __future__ import annotations
import pygame as pg
from collision_detector import CollisionDetector


class GroupWithCD(pg.sprite.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cd = CollisionDetector()

    def add_internal(self, sprite, layer=None):
        super().add_internal(sprite, layer)
        self.cd.add(sprite)

    def remove_internal(self, sprite):
        super().remove_internal(sprite)
        self.cd.remove(sprite)


ALL_ENEMIES: pg.sprite.Group = pg.sprite.Group()
ALL_PLAYERS: pg.sprite.Group = pg.sprite.Group()
ALL_COLLIDING_OBJECTS: GroupWithCD = GroupWithCD()
ALL_DRAWABLE_OBJECTS: pg.sprite.Group = pg.sprite.Group()
ALL_POWERUPS: GroupWithCD = GroupWithCD()
ALL_EXPLOSIONS: pg.sprite.Group = pg.sprite.Group()
ALL_UI_DRAWABLE_OBJECTS: pg.sprite.Group = pg.sprite.Group()
ALL_STATUSES: pg.sprite.Group = pg.sprite.Group()
ALL_ENGINES: pg.sprite.Group = pg.sprite.Group()
ALL_PARTICLES: pg.sprite.Group = pg.sprite.Group()
