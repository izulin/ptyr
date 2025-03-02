from __future__ import annotations

import pygame as pg


def with_outline(sprite: pg.Sprite, color: pg.Color):
    new_mask = sprite.mask.copy()
    sprite.mask.convolve(pg.Mask((3, 3), fill=1), new_mask, (-1, -1))
    s = new_mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    s.blit(sprite.image)
    return s
