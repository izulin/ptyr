from __future__ import annotations
import pygame as pg


class CachedSurface:
    _image_cache: list[pg.Surface]
    _mask_cache: list[pg.Mask]

    def __init__(self, image: pg.Surface):
        self._image_cache = [pg.transform.rotate(image, i) for i in range(360)]
        self._mask_cache = [pg.mask.from_surface(im) for im in self._image_cache]

    def get_image(self, ang: int = 0) -> pg.Surface:
        return self._image_cache[int(ang) % 360]

    def get_mask(self, ang: int = 0) -> pg.Mask:
        return self._mask_cache[int(ang) % 360]

    def get_rect(self, ang: int = 0, **kwargs):
        return self.get_image(ang).get_rect(**kwargs)


class CachedAnimation:
    _images: list[CachedSurface]

    def __init__(self, images: list[pg.Surface]):
        self._images = [CachedSurface(im) for im in images]

    def get_frame(self, i: int) -> CachedSurface:
        return self._images[int(i)]

    def __len__(self):
        return len(self._images)
