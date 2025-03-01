from __future__ import annotations
import pygame as pg
from collision_detector import CollisionDetector
from typing import Callable, TYPE_CHECKING

from consts import ALL_SHIFTS

if TYPE_CHECKING:
    from objects import Collides
from logger import logger


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


class GroupWithPriority(pg.sprite.Group):
    def sprites(self):
        return sorted(super().sprites(), key=lambda x: getattr(x, "priority", 0))


ALL_ENEMIES: pg.sprite.Group = pg.sprite.Group()
ALL_PLAYERS: pg.sprite.Group = pg.sprite.Group()
ALL_OBJECTS: pg.sprite.Group = pg.sprite.Group()
ALL_COLLIDING_OBJECTS: GroupWithCD = GroupWithCD()

ALL_DRAWABLE_OBJECTS: dict(tuple(int, int), pg.sprite.LayeredUpdates) = {
            (shift.x, shift.y): pg.sprite.LayeredUpdates()
            for shift in ALL_SHIFTS
        }

ALL_POWERUPS: GroupWithCD = GroupWithCD()
ALL_UI_DRAWABLE_OBJECTS: pg.sprite.Group = pg.sprite.Group()
ALL_WITH_UPDATE: GroupWithPriority = GroupWithPriority()


def try_and_spawn_object(
    func: Callable[[], Collides], num_copies: int, total_tries: int
):
    succ = []
    while total_tries > 0 and len(succ) < num_copies:
        obj: Collides = func()
        if ALL_COLLIDING_OBJECTS.cd.collide_with_callback(obj, on_collision=None):
            obj.kill()
        else:
            succ.append(obj)
        total_tries -= 1
    if len(succ) < num_copies:
        logger.info(f"spawned {type(obj).__qualname__} {len(succ)} out of {num_copies}")
    return succ
