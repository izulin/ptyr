from __future__ import annotations
import pygame as pg

from groups import ALL_DELAYED


class DelayedEvent(pg.sprite.Sprite):
    def __init__(self, action, delay, repeat=False, name=""):
        super().__init__(ALL_DELAYED)
        self.action = action
        self.t = delay
        self.delay = delay
        self.repeat = repeat
        self.name = name

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
