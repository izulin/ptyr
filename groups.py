from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame as pg

from collision_detector import CollisionDetector
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
    def __init__(self, *args, key: str, **kwargs):
        self.key = key
        super().__init__(*args, **kwargs)

    def sprites(self):
        return sorted(super().sprites(), key=lambda x: getattr(x, self.key, 0))


class LayeredUpdates(GroupWithPriority, pg.sprite.RenderUpdates):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, key="_layer")


ALL_ENEMIES: pg.sprite.Group = pg.sprite.Group()
ALL_PLAYERS: pg.sprite.Group = pg.sprite.Group()
ALL_COLLIDING_OBJECTS: GroupWithCD = GroupWithCD()
ALL_DRAWABLE_OBJECTS: dict(tuple(int, int), LayeredUpdates) = {
    (shift.x, shift.y): LayeredUpdates() for shift in ALL_SHIFTS
}
ALL_POWERUPS: GroupWithCD = GroupWithCD()
ALL_UI_DRAWABLE_OBJECTS: pg.sprite.Group = pg.sprite.Group()
ALL_WITH_UPDATE: GroupWithPriority = GroupWithPriority(key="priority")


def kill_all():
    for group in [
        ALL_ENEMIES,
        ALL_PLAYERS,
        ALL_COLLIDING_OBJECTS,
        *ALL_DRAWABLE_OBJECTS.values(),
        ALL_POWERUPS,
        ALL_UI_DRAWABLE_OBJECTS,
        ALL_WITH_UPDATE,
    ]:
        for sprite in group:
            sprite.kill()


def try_and_spawn_object(
    func: Callable[[], Collides],
    num_copies: int,
    total_tries: int,
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
