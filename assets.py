from __future__ import annotations
import pygame as pg
from consts import SCREEN_HEIGHT, SCREEN_WIDTH
from surface import CachedSurface, CachedAnimation


def load_from_file(
    posx: int, posy: int, sizex: int, sizey: int, filename: str
) -> pg.Surface:
    ret_surface = pg.Surface((sizex, sizey), flags=pg.SRCALPHA)
    image = pg.image.load(filename).convert_alpha()
    ret_surface.blit(image, (0, 0), (posx, posy, sizex, sizey))
    return remove_background(ret_surface)


def load_double_from_file(
    posx: int, posy: int, sizex: int, sizey: int, filename: str
) -> pg.Surface:
    ret_surface = pg.Surface((2 * sizex, sizey), flags=pg.SRCALPHA)
    image = pg.image.load(filename).convert_alpha()
    ret_surface.blit(image, (0, 0), (posx, posy, sizex, sizey))
    ret_surface.blit(image, (sizex, 0), (posx, posy + sizey, sizex, sizey))
    return remove_background(ret_surface)


def load_double_reversed_from_file(
    posx: int, posy: int, sizex: int, sizey: int, filename: str
) -> pg.Surface:
    ret_surface = pg.Surface((2 * sizex, sizey), flags=pg.SRCALPHA)
    image = pg.image.load(filename).convert_alpha()
    ret_surface.blit(image, (sizex, 0), (posx, posy, sizex, sizey))
    ret_surface.blit(image, (0, 0), (posx, posy + sizey, sizex, sizey))
    return remove_background(ret_surface)


def load_quad_from_file(
    posx: int, posy: int, sizex: int, sizey: int, filename: str
) -> pg.Surface:
    ret_surface = pg.Surface((2 * sizex, 2 * sizey), flags=pg.SRCALPHA)
    image = pg.image.load(filename).convert_alpha()
    ret_surface.blit(image, (0, 0), (posx, posy, sizex, sizey))
    ret_surface.blit(image, (sizex, 0), (posx, posy + sizey, sizex, sizey))
    ret_surface.blit(image, (0, sizey), (posx, posy + 2 * sizey, sizex, sizey))
    ret_surface.blit(image, (sizex, sizey), (posx, posy + 3 * sizey, sizex, sizey))
    return remove_background(ret_surface)


def remove_background(surface: pg.Surface) -> pg.Surface:
    """In place removal."""
    pxarray = pg.PixelArray(surface)
    pxarray.replace((191, 220, 191, 255), (0, 0, 0, 0), 0.001)
    return surface


PlayerImages = [
    CachedSurface(
        load_from_file(48, 58 + i * 27, 24, 27, "assets/tyrian/tyrian.shp.007D3C.png")
    )
    for i in range(6)
]
AsteroidLargeImages = [
    CachedSurface(load_from_file(2, 4, 42, 46, "assets/tyrian/newshd.shp.000000.png")),
    CachedSurface(load_from_file(79, 4, 40, 50, "assets/tyrian/newshd.shp.000000.png")),
]

AsteroidMediumImages = [
    CachedSurface(load_from_file(50, 1, 22, 20, "assets/tyrian/newshd.shp.000000.png")),
    CachedSurface(
        load_from_file(48, 29, 21, 23, "assets/tyrian/newshd.shp.000000.png")
    ),
    CachedSurface(
        load_from_file(96, 57, 24, 25, "assets/tyrian/newshd.shp.000000.png")
    ),
    CachedSurface(
        load_from_file(97, 86, 23, 23, "assets/tyrian/newshd.shp.000000.png")
    ),
    CachedSurface(
        load_from_file(194, 57, 22, 20, "assets/tyrian/newshd.shp.000000.png")
    ),
]

AsteroidSmallImages = [
    CachedSurface(
        load_from_file(216, 56, 12, 14, "assets/tyrian/newshd.shp.000000.png")
    ),
    CachedSurface(
        load_from_file(216, 70, 12, 14, "assets/tyrian/newshd.shp.000000.png")
    ),
    CachedSurface(
        load_from_file(216, 85, 12, 12, "assets/tyrian/newshd.shp.000000.png")
    ),
    CachedSurface(
        load_from_file(216, 98, 12, 15, "assets/tyrian/newshd.shp.000000.png")
    ),
]

BackgroundImage = pg.transform.scale(
    pg.image.load("assets/background.jpg").convert_alpha(),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)

SmallBulletImage = CachedSurface(
    load_from_file(183, 74, 5, 5, "assets/tyrian/newsh(.shp.000000.png")
)

SmallPlasmaImage = CachedSurface(
    load_from_file(15, 3, 5, 5, "assets/tyrian/tyrian.shp.01D8A7.png")
)

MediumExplosion = CachedAnimation(
    [
        load_quad_from_file(
            0 + 12 * i, 126, 12, 14, "assets/tyrian/tyrian.shp.01D8A7.png"
        )
        for i in range(11)
    ],
    animation_time=1_000,
    loops=False,
)

LargeExplosion1 = CachedAnimation(
    [
        load_double_from_file(
            0 + 12 * i, -2, 12, 28, "assets/tyrian/newsh6.shp.000000.png"
        )
        for i in range(17)
    ],
    animation_time=1_000,
    loops=False,
)

LargeExplosion2 = CachedAnimation(
    [
        load_double_reversed_from_file(
            0 + 12 * i, 112, 12, 28, "assets/tyrian/newsh6.shp.000000.png"
        )
        for i in range(13)
    ],
    animation_time=1_000,
    loops=False,
)

MineAnimation = CachedAnimation(
    [
        load_from_file(192, 113 + 28 * i, 22, 22, "assets/tyrian/newsha.shp.000000.png")
        for i in range(3)
    ],
    animation_time=3_000,
    loops=True,
)

HealPowerupImage = CachedSurface(
    load_from_file(171, 115, 19, 22, "assets/tyrian/newsh1.shp.000000.png")
)

SingleShotWeaponImage = CachedSurface(
    load_from_file(170, 143, 20, 21, "assets/tyrian/tyrian.shp.010008.png")
)

DoubleShotWeaponImage = CachedSurface(
    load_from_file(194, 143, 20, 21, "assets/tyrian/tyrian.shp.010008.png")
)

MineLauncherWeaponImage = CachedSurface(
    load_from_file(2, 199, 20, 21, "assets/tyrian/tyrian.shp.010008.png")
)
