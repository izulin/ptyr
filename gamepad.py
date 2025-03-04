from __future__ import annotations

from pygame._sdl2 import controller

from logger import logger

controller.init()
logger.info(f"Num of controllers: {controller.get_count()}")


class MockController:
    def get_button(self, i: int):
        return False

    def get_axis(self, *args, **kwargs):
        return 0


def get_gamepad(player_id: int):
    try:
        return controller.Controller(player_id - 1)
    except:  # noqa E722
        return MockController()
