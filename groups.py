from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame as pg
from pygame import Vector3

from consts import ALL_SHIFTS
from spatial import Spatial

if TYPE_CHECKING:
    from objects import Collides, DrawableObject
from logger import logger


class GroupWithCD(pg.sprite.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spatial = Spatial(builder=set, subx=100, suby=100)

    def add_internal(self, sprite, layer=None):
        super().add_internal(sprite, layer)
        self.spatial.add(sprite)

    def remove_internal(self, sprite):
        super().remove_internal(sprite)
        self.spatial.remove(sprite)

    def move(self, sprite: DrawableObject, rect_a: pg.Rect, rect_b: pg.Rect):
        self.spatial.move(sprite, rect_a, rect_b)

    def _collide_with_callback(
        self,
        sprite: DrawableObject,
        *,
        on_collision=None,
    ) -> list[DrawableObject]:
        ret = []
        seen = {sprite}
        for bucket in self.spatial.all_buckets(sprite.rect):
            for other in bucket:
                if other in seen:
                    continue
                seen.add(other)
                if pg.sprite.collide_rect(sprite, other) and pg.sprite.collide_mask(
                    sprite,
                    other,
                ):
                    ret.append(other)
                    if on_collision is None:
                        return ret
                    on_collision(sprite, other)
        return ret

    def collide_with_callback(
        self,
        sprite: DrawableObject,
        *,
        on_collision=None,
    ) -> list[DrawableObject]:
        ret = []
        for shift in ALL_SHIFTS:
            sprite.pos += Vector3(shift.x, shift.y, 0)
            sprite.rect.move_ip(shift)
            ret.extend(self._collide_with_callback(sprite, on_collision=on_collision))
            sprite.pos -= Vector3(shift.x, shift.y, 0)
            sprite.rect.move_ip(-shift)
            if ret and on_collision is None:
                return ret
        return ret


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
ALL_DRAWABLE_OBJECTS: dict[tuple(int, int), LayeredUpdates] = {
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
        if ALL_COLLIDING_OBJECTS.collide_with_callback(obj, on_collision=None):
            obj.kill()
        else:
            succ.append(obj)
        total_tries -= 1
    if len(succ) < num_copies:
        logger.info(f"spawned {type(obj).__qualname__} {len(succ)} out of {num_copies}")
    return succ
