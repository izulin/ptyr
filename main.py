from __future__ import annotations
import pygame as pg
import sys

from timers import TIMERS, Timer
from logger import logger

with Timer("pg.init"):
    import pg_init  # noqa: F401

from text import display_text
from consts import FPS, BLACK, ALL_SHIFTS
from delayed import DelayedEvent
from display import DISPLAYSURF, ALL_CHANGES_DISPLAYSURF
from players import spawn_player
from enemies import spawn_asteroid
from groups import (
    ALL_ENEMIES,
    ALL_COLLIDING_OBJECTS,
    ALL_PLAYERS,
    ALL_DRAWABLE_OBJECTS,
    ALL_POWERUPS,
    ALL_UI_DRAWABLE_OBJECTS,
    ALL_WITH_UPDATE,
    ALL_OBJECTS,
)
from collision_logic import (
    _colliding_colliding_logic,
    _player_powerup_logic,
)

from assets import BackgroundImage

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import Object


DISPLAYSURF.blit(BackgroundImage, (0, 0))


class Game:
    def __init__(self):
        self.SHOW_SPEEDS = False
        self.SHOW_HP = 1
        self.FramePerSec = pg.time.Clock()
        self.done = False

        pg.display.set_caption("Project Iapetus")

        with Timer("Game state init"):
            spawn_player(1)
            spawn_player(2)

            while len(ALL_ENEMIES) < 10:
                spawn_asteroid()

        DelayedEvent(
            lambda: spawn_asteroid() if len(ALL_ENEMIES) < 30 else None,
            5000,
            repeat=True,
            name="spawn_asteroid",
        )

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.done = True
                elif event.key == pg.K_BACKSPACE:
                    self.SHOW_SPEEDS = not self.SHOW_SPEEDS
                elif event.key == pg.K_EQUALS:
                    self.SHOW_HP = (self.SHOW_HP + 1) % 3

    def stats(self):
        self.cnt = getattr(self, "cnt", 0) + 1
        if self.cnt % 1000 == 0:
            total = Timer()
            total.cnt = 1000
            total.val = sum(timer.val for timer in TIMERS.values())
            logger.info(
                f"total:{total} " + " ".join(f"{k}:{v}" for k, v in TIMERS.items())
            )
            for t in TIMERS.values():
                t.reset()

    def updates(self, dt: float):
        ALL_WITH_UPDATE.update(dt)
        for sprite in ALL_OBJECTS:
            if not sprite.alive_state:
                sprite.kill()
                sprite.on_death()

    def collisions(self):
        for sprite in ALL_COLLIDING_OBJECTS:
            ALL_COLLIDING_OBJECTS.cd.collide_with_callback(
                sprite, on_collision=_colliding_colliding_logic
            )
        for player in ALL_PLAYERS:
            ALL_POWERUPS.cd.collide_with_callback(
                player, on_collision=_player_powerup_logic
            )

    def main(self):
        while not self.done:
            self.event_loop()

            with TIMERS["clears"]:
                for g in ALL_DRAWABLE_OBJECTS.values():
                    g.clear(DISPLAYSURF, BackgroundImage)
            with TIMERS["blits"]:
                for change in ALL_CHANGES_DISPLAYSURF:
                    DISPLAYSURF.blit(BackgroundImage, change, change)

            ALL_CHANGES_DISPLAYSURF.clear()

            with TIMERS["draw"]:
                for shift in ALL_SHIFTS:
                    for sprite in ALL_DRAWABLE_OBJECTS[(shift.x, shift.y)]:
                        sprite.rect.move_ip(shift)
                    ALL_DRAWABLE_OBJECTS[(shift.x, shift.y)].draw(DISPLAYSURF)
                    for sprite in ALL_DRAWABLE_OBJECTS[(shift.x, shift.y)]:
                        sprite.rect.move_ip(-shift)

            with TIMERS["debugs"]:
                if self.SHOW_SPEEDS:
                    sprite: Object
                    for sprite in ALL_DRAWABLE_OBJECTS:
                        try:
                            sprite.draw_debugs()
                        except AttributeError:
                            pass

            with TIMERS["UX"]:
                if self.SHOW_HP == 2:
                    sprite: Object
                    for sprite in ALL_UI_DRAWABLE_OBJECTS:
                        sprite.draw_ui()
                elif self.SHOW_HP == 1:
                    for player in ALL_PLAYERS:
                        player.draw_ui()

            fps = self.FramePerSec.get_fps()

            display_text(f"{fps:.2f}.", BLACK, (10, 10))

            with TIMERS["flip"]:
                pg.display.flip()

            dt = self.FramePerSec.tick(FPS)

            with TIMERS["updates"]:
                self.updates(dt)

            with TIMERS["collisions"]:
                self.collisions()

            self.stats()


Game().main()


logger.info("Finished")
pg.quit()
sys.exit()
