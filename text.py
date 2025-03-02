from __future__ import annotations

import pygame as pg

from config import CONFIG
from consts import WHITE
from display import ALL_CHANGES_DISPLAYSURF, DISPLAYSURF

fonts = {}
for bold in [False, True]:
    for size in range(1, 6):
        fonts[(bold, size)] = pg.font.SysFont(
            "Lucida Console", int((CONFIG.SCREEN_HEIGHT / 50) * size), bold=bold
        )


def display_text(
    text: str,
    pos: tuple[int, int],
    *,
    color: pg.Color = WHITE,
    bold=False,
    size: int = 1,
):
    render = fonts[(bold, size)].render(text, True, color)
    ALL_CHANGES_DISPLAYSURF.append(DISPLAYSURF.blit(render, pos))
