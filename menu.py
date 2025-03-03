from __future__ import annotations

import pygame as pg

from assets import RightArrowImage
from config import CONFIG
from display import ALL_CHANGES_DISPLAYSURF, DISPLAYSURF
from game_state import init_game_state
from groups import kill_all
from text import display_text


class MenuElement:
    def take_action(self):
        raise NotImplementedError

    def draw(self, pos: tuple[int, int]):
        raise NotImplementedError


class TextMenuElement(MenuElement):
    text: str

    def __init__(self, text: str | None = None):
        if text is not None:
            self.text = text

    def draw(self, pos: tuple[int, int]):
        display_text(self.text, pos, size=3)


class ConfigMenuElement(MenuElement):
    option: str

    def __init__(self, option: str | None = None):
        if option is not None:
            self.option = option

    def draw(self, pos: tuple[int, int]):
        posx, posy = pos
        display_text(self.option, pos, size=3)
        display_text(
            str(getattr(CONFIG, self.option)),
            (posx + CONFIG.SCREEN_WIDTH / 2, posy),
            size=3,
        )


class NumOfPlayersMenuElement(ConfigMenuElement):
    option = "NUM_OF_PLAYERS"

    def take_action(self):
        CONFIG.NUM_OF_PLAYERS += 1
        if CONFIG.NUM_OF_PLAYERS > 4:
            CONFIG.NUM_OF_PLAYERS = 1


class ShowHPMenuElement(ConfigMenuElement):
    option = "SHOW_HP"

    def take_action(self):
        CONFIG.SHOW_HP = (CONFIG.SHOW_HP + 1) % 3


class RestartElement(TextMenuElement):
    text = "RESTART"

    def take_action(self):
        MENU_STACK.clear()
        kill_all()
        init_game_state()


class OptionsElement(TextMenuElement):
    text = "OPTIONS"

    def take_action(self):
        MENU_STACK.append(Menu(NumOfPlayersMenuElement(), ShowHPMenuElement()))


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
            ),
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
    return Menu(RestartElement(), OptionsElement(), QuitElement())


MENU_STACK: list[Menu] = []
