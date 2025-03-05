from __future__ import annotations

from functools import cached_property

import pygame as pg
from pygame import Vector2

from timers import timeit


def mask_centroid(mask: pg.Mask) -> Vector2:
    x_size, y_size = mask.get_size()
    xacc, yacc, cnt = 0, 0, 0
    for x in range(x_size):
        for y in range(y_size):
            if mask.get_at((x, y)):
                xacc += x
                yacc += y
                cnt += 1
    return Vector2(xacc / cnt, yacc / cnt)


class CachedSurface:
    _image_cache: list[pg.Surface]
    _mask_cache: list[pg.Mask]
    _centroids: list[Vector2]
    _no_rotation: bool

    def __init__(self, image: pg.Surface, no_rotation=False):
        if no_rotation:
            self._image_cache = [image]
            mask = pg.mask.from_surface(image)
            self._mask_cache = [mask]
            self._centroids = [mask_centroid(mask)]
        else:
            self._image_cache = [pg.transform.rotate(image, i) for i in range(360)]
            self._mask_cache = [pg.mask.from_surface(im) for im in self._image_cache]
            self._centroids = [None for mask in self._mask_cache]
        self._no_rotation = no_rotation

    @cached_property
    def inertia_moment_coef(self) -> float:
        mask = self.get_mask(0)
        x_size, y_size = mask.get_size()
        x2acc, xacc, y2acc, yacc, cnt = 0, 0, 0, 0, 0
        for x in range(x_size):
            for y in range(y_size):
                if mask.get_at((x, y)):
                    x2acc += x**2
                    y2acc += y**2
                    xacc += x
                    yacc += y
                    cnt += 1

        return x2acc / cnt - (xacc / cnt) ** 2 + y2acc / cnt - (yacc / cnt) ** 2

    def get_image(self, ang: int = 0) -> pg.Surface:
        if self._no_rotation:
            return self._image_cache[0]
        else:
            return self._image_cache[int(ang)]

    def get_mask(self, ang: int = 0) -> pg.Mask:
        if self._no_rotation:
            return self._mask_cache[0]
        else:
            return self._mask_cache[int(ang)]

    def get_rect(self, ang: int = 0, **kwargs):
        return self.get_image(ang).get_rect(**kwargs)

    @timeit("CENTROID")
    def get_centroid(self, ang: int = 0) -> Vector2:
        if self._no_rotation:
            return self._centroids[0]
        else:
            ret = self._centroids[ang]
            if ret is None:
                ret = mask_centroid(self.get_mask(ang))
                self._centroids[ang] = ret
            return ret

    def scale(self, size) -> CachedSurface:
        return CachedSurface(
            pg.transform.scale(self.get_image(), size),
            no_rotation=self._no_rotation,
        )

    def scale_by(self, factor: float) -> CachedSurface:
        return CachedSurface(
            pg.transform.scale_by(self.get_image(), factor),
            no_rotation=self._no_rotation,
        )


class CachedAnimation:
    images: list[CachedSurface]
    animation_time: int
    loops: bool

    def __init__(self, images: list[pg.Surface], animation_time: int, loops: bool):
        self.images = [CachedSurface(im) for im in images]
        self.animation_time = animation_time
        self.loops = loops

    def get_frame(self, time: float) -> CachedSurface:
        frame = int(time / (self.animation_time / len(self)))
        if self.loops:
            return self.images[frame % len(self)]
        else:
            return self.images[min(frame, len(self) - 1)]

    def __len__(self):
        return len(self.images)

    def scale_by(self, factor: float, slowdown: float = 1.0) -> CachedAnimation:
        return CachedAnimation(
            [pg.transform.scale_by(s.get_image(), factor) for s in self.images],
            int(self.animation_time * slowdown),
            self.loops,
        )
