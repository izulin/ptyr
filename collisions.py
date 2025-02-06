from __future__ import annotations
import pygame
from pygame import Vector3

from consts import ALL_SHIFTS
from collections import defaultdict

from math_utils import test_if_proper_collision


class CollisionDetector:
    def __init__(self, *sprites: pygame.sprite.Sprite):
        self.subs = 100
        self._division: dict[tuple[int, int], pygame.sprite.Sprite] = defaultdict(list)
        for sprite in sprites:
            self.add(sprite)

    def add(self, sprite: pygame.sprite.Sprite):
        rect: pygame.Rect = sprite.rect
        for x in set([rect.left, rect.right]):
            for y in set([rect.top, rect.bottom]):
                self._division[(x // self.subs, y // self.subs)].append(sprite)

    def _collide_with_callback(
        self, sprite: pygame.sprite.Sprite, *, on_collision=None, stationary
    ) -> bool:
        rect: pygame.Rect = sprite.rect
        r: list[pygame.sprite.Sprite] = []
        for x in set([rect.left, rect.right]):
            for y in set([rect.top, rect.bottom]):
                r.extend(self._division[(x // self.subs, y // self.subs)])
        ret = False
        for other in set(r):
            if sprite == other:
                continue
            if pygame.sprite.collide_rect(sprite, other) and pygame.sprite.collide_mask(
                sprite, other
            ):
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
            sprite.pos += Vector3(shift.x, shift.y, 0)
            sprite.rect.move_ip(shift)
            ret = self._collide_with_callback(
                sprite, on_collision=on_collision, stationary=stationary
            )
            sprite.pos -= Vector3(shift.x, shift.y, 0)
            sprite.rect.move_ip(-shift)
            if ret and on_collision is None:
                return True
        return ret
