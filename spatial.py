from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    import pygame as pg

    from objects import DrawableObject


class Spatial:
    def __init__(
        self,
        *sprites: DrawableObject,
        builder: Callable,
        subx: int,
        suby: int,
    ):
        self.subx = subx
        self.suby = suby
        self.buckets: dict = defaultdict(builder)
        for sprite in sprites:
            self.add(sprite)

    def add(self, sprite: DrawableObject):
        for bucket in self.all_buckets(sprite.rect):
            bucket.add(sprite)

    def remove(self, sprite: DrawableObject):
        for bucket in self.all_buckets(sprite.rect):
            bucket.remove(sprite)

    def move(self, sprite: DrawableObject, rect_a: pg.Rect, rect_b: pg.Rect):
        x_start_a = rect_a.left // self.subx
        x_end_a = rect_a.right // self.subx
        y_start_a = rect_a.top // self.suby
        y_end_a = rect_a.bottom // self.suby
        x_start_b = rect_b.left // self.subx
        x_end_b = rect_b.right // self.subx
        y_start_b = rect_b.top // self.suby
        y_end_b = rect_b.bottom // self.suby
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
                self.buckets[(x, y)].add(sprite)
        for x in range(x_start_b, x_end_b + 1):
            for y in range(y_start_b, y_end_b + 1):
                if x_start_a <= x <= x_end_a and y_start_a <= y <= y_end_a:
                    continue
                self.buckets[(x, y)].remove(sprite)

    def all_buckets(self, rect: pg.Rect):
        x_start = rect.left // self.subx
        x_end = rect.right // self.subx
        y_start = rect.top // self.suby
        y_end = rect.bottom // self.suby
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                yield self.buckets[(x, y)]
