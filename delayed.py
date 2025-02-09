from __future__ import annotations
import pygame

ALL_DELAYED = pygame.sprite.Group()


class DelayedEvent(pygame.sprite.Sprite):
    def __init__(self, action, delay, repeat=False):
        super().__init__()
        self.action = action
        self.t = delay
        self.delay = delay
        self.add(ALL_DELAYED)
        self.repeat = repeat

    def update(self, dt):
        self.t -= dt
        if self.t < 0:
            self.action()
            if self.repeat:
                self.t += self.delay
            else:
                self.kill()
