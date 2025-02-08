from __future__ import annotations
import pygame
from pygame import Vector3

from consts import ALL_SHIFTS
from collections import defaultdict

from math_utils import test_if_proper_collision


class CollisionDetector:
    def __init__(self, *sprites: pygame.sprite.Sprite):
        self.subs = 100
        self._division: dict[tuple[int, int], set[pygame.sprite.Sprite]] = defaultdict(
            set
        )
        for sprite in sprites:
            self.add(sprite)

    def add(self, sprite: pygame.sprite.Sprite):
        rect: pygame.Rect = sprite.rect
        x_start = rect.left // self.subs
        x_end = rect.right // self.subs
        y_start = rect.top // self.subs
        y_end = rect.bottom // self.subs
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                self._division[(x, y)].add(sprite)

    def remove(self, sprite: pygame.sprite.Sprite):
        rect: pygame.Rect = sprite.rect
        x_start = rect.left // self.subs
        x_end = rect.right // self.subs
        y_start = rect.top // self.subs
        y_end = rect.bottom // self.subs
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                self._division[(x, y)].remove(sprite)

    def move(
        self, sprite: pygame.sprite.Sprite, rect_a: pygame.Rect, rect_b: pygame.Rect
    ):
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
        self, sprite: pygame.sprite.Sprite, *, on_collision=None, stationary
    ) -> bool:
        rect: pygame.Rect = sprite.rect
        x_start = rect.left // self.subs
        x_end = rect.right // self.subs
        y_start = rect.top // self.subs
        y_end = rect.bottom // self.subs
        ret = False
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                for other in self._division[(x, y)]:
                    if (
                        sprite == other
                        or (x > x_start and other.rect.left < x * self.subs)
                        or (y < y_start and other.rect.top < y * self.subs)
                    ):
                        continue
                    if pygame.sprite.collide_rect(
                        sprite, other
                    ) and pygame.sprite.collide_mask(sprite, other):
                        if stationary or test_if_proper_collision(sprite, other):
                            ret = True
                            if on_collision is None:
                                return True
                            on_collision(sprite, other)
        return ret

    def collide_with_callback(
        self, sprite: pygame.sprite.Sprite, *, on_collision=None, stationary
    ) -> bool:
        ret = False
        for shift in ALL_SHIFTS:
            sprite.pos += Vector3(*shift, 0)
            sprite.rect.move_ip(shift)
            ret = self._collide_with_callback(
                sprite, on_collision=on_collision, stationary=stationary
            )
            sprite.pos -= Vector3(*shift, 0)
            sprite.rect.move_ip(-shift)
            if ret and on_collision is None:
                return True
        return ret


ALL_SPRITES_CD = CollisionDetector()
