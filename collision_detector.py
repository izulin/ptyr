from __future__ import annotations
import pygame as pg
from pygame.math import Vector3

from consts import ALL_SHIFTS
from collections import defaultdict


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import DrawableObject


class CollisionDetector:
    def __init__(self, *sprites: DrawableObject):
        self.subs = 100
        self._division: dict[tuple[int, int], set[DrawableObject]] = defaultdict(set)
        for sprite in sprites:
            self.add(sprite)

    def add(self, sprite: DrawableObject):
        rect: pg.Rect = sprite.rect
        x_start = rect.left // self.subs
        x_end = rect.right // self.subs
        y_start = rect.top // self.subs
        y_end = rect.bottom // self.subs
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                self._division[(x, y)].add(sprite)

    def remove(self, sprite: DrawableObject):
        rect: pg.Rect = sprite.rect
        x_start = rect.left // self.subs
        x_end = rect.right // self.subs
        y_start = rect.top // self.subs
        y_end = rect.bottom // self.subs
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                self._division[(x, y)].remove(sprite)

    def move(self, sprite: DrawableObject, rect_a: pg.Rect, rect_b: pg.Rect):
        x_start_a = rect_a.left // self.subs
        x_end_a = rect_a.right // self.subs
        y_start_a = rect_a.top // self.subs
        y_end_a = rect_a.bottom // self.subs
        x_start_b = rect_b.left // self.subs
        x_end_b = rect_b.right // self.subs
        y_start_b = rect_b.top // self.subs
        y_end_b = rect_b.bottom // self.subs
        if (
            x_start_a == x_start_b
            and x_end_a == x_end_b
            and y_start_a == y_start_b
            and y_end_a == y_end_b
        ):
            return
        for x in range(x_start_a, x_end_a + 1):
            for y in range(y_start_a, y_end_a + 1):
                if x_start_b <= x <= x_end_b and y_start_b <= y <= y_end_b:
                    continue
                self._division[(x, y)].add(sprite)
        for x in range(x_start_b, x_end_b + 1):
            for y in range(y_start_b, y_end_b + 1):
                if x_start_a <= x <= x_end_a and y_start_a <= y <= y_end_a:
                    continue
                self._division[(x, y)].remove(sprite)

    def _collide_with_callback(
        self, sprite: DrawableObject, *, on_collision=None
    ) -> list[DrawableObject]:
        rect: pg.Rect = sprite.rect
        x_start = rect.left // self.subs
        x_end = rect.right // self.subs
        y_start = rect.top // self.subs
        y_end = rect.bottom // self.subs
        ret = []
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                for other in self._division[(x, y)]:
                    if (
                        sprite == other
                        or (x > x_start and other.rect.left < x * self.subs)
                        or (y < y_start and other.rect.top < y * self.subs)
                    ):
                        continue
                    if pg.sprite.collide_rect(sprite, other) and pg.sprite.collide_mask(
                        sprite, other
                    ):
                        ret.append(other)
                        if on_collision is None:
                            return ret
                        on_collision(sprite, other)
        return ret

    def collide_with_callback(
        self, sprite: DrawableObject, *, on_collision=None
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
