from __future__ import annotations
import pygame as pg
from pygame import Vector2
from functools import cached_property


class CachedSurface:
    _image_cache: list[pg.Surface]
    _mask_cache: list[pg.Mask]
    _centroids: list[Vector2]
    inertia_moment_coef: float

    def __init__(self, image: pg.Surface):
        self._image_cache = [pg.transform.rotate(image, i) for i in range(360)]
        self._mask_cache = [pg.mask.from_surface(im) for im in self._image_cache]

    @cached_property
    def inertia_moment_coef(self):
        def avg(l):
            return sum(l) / len(l)

        mask = self._mask_cache[0]
        x_size, y_size = mask.get_size()
        return (
            avg(
                [
                    x**2
                    for x in range(x_size)
                    for y in range(y_size)
                    if mask.get_at((x, y))
                ]
            )
            + avg(
                [
                    y**2
                    for x in range(x_size)
                    for y in range(y_size)
                    if mask.get_at((x, y))
                ]
            )
            - avg(
                [x for x in range(x_size) for y in range(y_size) if mask.get_at((x, y))]
            )
            ** 2
            - avg(
                [y for x in range(x_size) for y in range(y_size) if mask.get_at((x, y))]
            )
            ** 2
        )

    def get_image(self, ang: int = 0) -> pg.Surface:
        return self._image_cache[int(ang) % 360]

    def get_mask(self, ang: int = 0) -> pg.Mask:
        return self._mask_cache[int(ang) % 360]

    def get_rect(self, ang: int = 0, **kwargs):
        return self.get_image(ang).get_rect(**kwargs)

    def get_centroid(self, ang: int = 0) -> Vector2:
        return Vector2(self.get_mask(ang).centroid())

    def scale(self, size) -> pg.Surface:
        return pg.transform.scale(self.get_image(), size)


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

    def scale_by(self, factor: float, slowdown: float):
        return CachedAnimation(
            [pg.transform.scale_by(s.get_image(), factor) for s in self.images],
            self.animation_time * slowdown,
            self.loops,
        )
