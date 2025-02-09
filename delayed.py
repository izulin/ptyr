from __future__ import annotations
import pygame as pg
import logging

logger = logging.getLogger(__name__)

ALL_DELAYED = pg.sprite.Group()


class DelayedEvent(pg.sprite.Sprite):
    def __init__(self, action, delay, repeat=False, name=""):
        super().__init__()
        self.action = action
        self.t = delay
        self.delay = delay
        self.add(ALL_DELAYED)
        self.repeat = repeat
        self.name = name
        logger.info(f"creating {self}")

    def update(self, dt):
        self.t -= dt
        if self.t < 0:
            logger.info(f"firing {self}")
            self.action()
            if self.repeat:
                self.t += self.delay
            else:
                self.kill()

    def __repr__(self):
        return f"Action({self.name}, {self.repeat})"
