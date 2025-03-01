from __future__ import annotations
import pygame as pg

from groups import ALL_WITH_UPDATE


class DelayedEvent(pg.sprite.Sprite):
    def __init__(self, action, delay, repeat=False, name=""):
        super().__init__(ALL_WITH_UPDATE)
        self.action = action
        self.t = delay
        self.delay = delay
        self.repeat = repeat
        self.name = name
        self.priority = -2

    def update(self, dt):
        self.t -= dt
        if self.t < 0:
            self.action()
            if self.repeat:
                self.t += self.delay
            else:
                self.kill()

    def __repr__(self):
        return f"Action({self.name}, {self.repeat})"
