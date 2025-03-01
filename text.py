from __future__ import annotations
import pygame as pg

from display import ALL_CHANGES_DISPLAYSURF, DISPLAYSURF

font = pg.font.SysFont("Lucida Console", 60)
font_small = pg.font.SysFont("Lucida Console", 20)


def display_text(text: str, color: pg.Color, pos: tuple[int,int]):
    render = font_small.render(text, True, color)
    ALL_CHANGES_DISPLAYSURF.append(DISPLAYSURF.blit(render, pos))