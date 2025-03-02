from __future__ import annotations

import pygame as pg

from assets import RightArrowImage
from config import CONFIG
from display import ALL_CHANGES_DISPLAYSURF, DISPLAYSURF
from text import display_text


class MenuElement:
    def take_action(self):
        raise NotImplementedError

    def draw(self, pos: tuple[int, int]):
        raise NotImplementedError


class TextMenuElement(MenuElement):
    text: str

    def __init__(self, text: str = None):
        if text is not None:
            self.text = text

    def draw(self, pos: tuple[int, int]):
        display_text(self.text, pos, size=3)


class RestartElement(TextMenuElement):
    text = "RESTART"

    def take_action(self):
        MENU_STACK.clear()


class QuitElement(TextMenuElement):
    text = "QUIT"

    def take_action(self):
        pg.event.post(pg.Event(pg.QUIT))


class Menu:
    items: list[MenuElement]

    def __init__(self, *items: MenuElement):
        self.items = items
        self.attention = 0

    def draw(self, pos: tuple[int, int]):
        posx, posy = pos
        step_y = CONFIG.SCREEN_HEIGHT / 5
        for i, item in enumerate(self.items):
            item.draw((posx, posy + i * step_y))

        ALL_CHANGES_DISPLAYSURF.append(
            DISPLAYSURF.blit(
                RightArrowImage,
                (posx - CONFIG.SCREEN_WIDTH / 10, posy + self.attention * step_y),
            )
        )

    def take_action(self):
        self.items[self.attention].take_action()

    def up(self):
        self.attention -= 1
        self.attention %= len(self.items)

    def down(self):
        self.attention += 1
        self.attention %= len(self.items)


def init_menu():
    return Menu(RestartElement(), QuitElement())


MENU_STACK: list[Menu] = []
