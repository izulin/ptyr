from __future__ import annotations
import pygame
from consts import SCREEN_HEIGHT, SCREEN_WIDTH


def load_from_file(
    posx: int, posy: int, sizex: int, sizey: int, filename: str
) -> pygame.Surface:
    ret_surface = pygame.Surface((sizex, sizey), flags=pygame.SRCALPHA)
    image = pygame.image.load(filename).convert_alpha()
    ret_surface.blit(image, (0, 0), (posx, posy, sizex, sizey))
    return remove_background(ret_surface)


def remove_background(surface: pygame.Surface) -> pygame.Surface:
    """In place removal."""
    pxarray = pygame.PixelArray(surface)
    pxarray.replace((191, 220, 191, 255), (0, 0, 0, 0), 0.001)
    return surface


PlayerImages = [
    load_from_file(48, 58 + i * 27, 24, 27, "assets/tyrian/tyrian.shp.007D3C.png")
    for i in range(6)
]
AsteroidLargeImage = load_from_file(0, 0, 45, 48, "assets/tyrian/newshd.shp.000000.png")

BackgroundImage = pygame.transform.scale(
    pygame.image.load("assets/background.jpg").convert_alpha(),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)

SmallPlasmaImage = load_from_file(15, 3, 5, 5, "assets/tyrian/tyrian.shp.01D8A7.png")


def load_quad_from_file(
    posx: int, posy: int, sizex: int, sizey: int, filename: str
) -> pygame.Surface:
    ret_surface = pygame.Surface((2 * sizex, 2 * sizey), flags=pygame.SRCALPHA)
    image = pygame.image.load(filename).convert_alpha()
    ret_surface.blit(image, (0, 0), (posx, posy, sizex, sizey))
    ret_surface.blit(image, (sizex, 0), (posx, posy + sizey, sizex, sizey))
    ret_surface.blit(image, (0, sizey), (posx, posy + 2 * sizey, sizex, sizey))
    ret_surface.blit(image, (sizex, sizey), (posx, posy + 3 * sizey, sizex, sizey))
    return remove_background(ret_surface)


ExplosionImage = load_quad_from_file(
    0, 126, 12, 14, "assets/tyrian/tyrian.shp.01D8A7.png"
)
