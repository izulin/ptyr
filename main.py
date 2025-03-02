from __future__ import annotations

import sys
from collections import defaultdict

import pygame as pg

from logger import logger
from timers import TIMERS, Timer

with Timer("pg.init"):
    import pg_init  # noqa: F401

from display import ALL_CHANGES_DISPLAYSURF, DISPLAYSURF  # noqa: I001

from typing import TYPE_CHECKING

from game_state import init_game_state
from assets import BackgroundImage
from collision_logic import (
    _colliding_colliding_logic,
    _player_powerup_logic,
)
from config import CONFIG
from consts import ALL_SHIFTS
from groups import (
    ALL_COLLIDING_OBJECTS,
    ALL_DRAWABLE_OBJECTS,
    ALL_PLAYERS,
    ALL_POWERUPS,
    ALL_UI_DRAWABLE_OBJECTS,
    ALL_WITH_UPDATE,
)
from menu import MENU_STACK, init_menu
from text import display_text

if TYPE_CHECKING:
    from objects import Object


DISPLAYSURF.blit(BackgroundImage, (0, 0))


class Game:
    def __init__(self):
        self.FramePerSec = pg.time.Clock()
        self.done = False
        self.cnt = 0
        self.object_count = defaultdict(int)

        pg.display.set_caption("Project Iapetus")
        init_game_state()

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if MENU_STACK:
                    if event.key == pg.K_ESCAPE:
                        MENU_STACK.pop()
                    elif event.key == pg.K_UP:
                        MENU_STACK[-1].up()
                    elif event.key == pg.K_DOWN:
                        MENU_STACK[-1].down()
                    elif event.key == pg.K_RETURN:
                        MENU_STACK[-1].take_action()
                else:
                    if event.key == pg.K_ESCAPE:
                        MENU_STACK.append(init_menu())

    def stats(self):
        self.cnt += 1
        for t in TIMERS.values():
            t.click()
        if TIMERS["TOTAL"].val >= 1:
            for k, v in sorted(TIMERS.items(), key=lambda x: x[1].val, reverse=True):
                logger.info(f"{k}:{v}")
            logger.info(
                " ".join(
                    f"{k}:{v / self.cnt:.1f}" for k, v in self.object_count.items()
                ),
            )
            for t in TIMERS.values():
                t.reset()
            self.cnt = 0
            self.object_count = defaultdict(int)

    def updates(self, dt: float):
        for sprite in ALL_WITH_UPDATE:
            with TIMERS[f"updates:{sprite.__class__.__qualname__}"]:
                sprite.update(dt)
                self.object_count[sprite.__class__.__qualname__] += 1
        for sprite in ALL_WITH_UPDATE:
            try:
                if not sprite.alive_state:
                    sprite.kill()
                    sprite.on_death()
            except AttributeError:  # noqa: PERF203
                pass

    @staticmethod
    def collisions():
        for sprite in ALL_COLLIDING_OBJECTS:
            ALL_COLLIDING_OBJECTS.cd.collide_with_callback(
                sprite,
                on_collision=_colliding_colliding_logic,
            )
        for player in ALL_PLAYERS:
            ALL_POWERUPS.cd.collide_with_callback(
                player,
                on_collision=_player_powerup_logic,
            )

    def main(self):
        while not self.done:
            with TIMERS["TOTAL"]:
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
                        with TIMERS["draw::move_ip"]:
                            for sprite in ALL_DRAWABLE_OBJECTS[(shift.x, shift.y)]:
                                sprite.rect.move_ip(shift)
                        ALL_DRAWABLE_OBJECTS[(shift.x, shift.y)].draw(DISPLAYSURF)
                        with TIMERS["draw::move_ip"]:
                            for sprite in ALL_DRAWABLE_OBJECTS[(shift.x, shift.y)]:
                                sprite.rect.move_ip(-shift)

                with TIMERS["UX"]:
                    if CONFIG.SHOW_HP == 2:
                        sprite: Object
                        for sprite in ALL_UI_DRAWABLE_OBJECTS:
                            sprite.draw_ui()
                    elif CONFIG.SHOW_HP == 1:
                        for player in ALL_PLAYERS:
                            player.draw_ui()

                fps = self.FramePerSec.get_fps()

                display_text(f"{fps:.2f}.", (10, 10))

                if MENU_STACK:
                    MENU_STACK[-1].draw(
                        (CONFIG.SCREEN_WIDTH / 3, CONFIG.SCREEN_HEIGHT / 10),
                    )

                with TIMERS["flip"]:
                    pg.display.flip()

                dt = self.FramePerSec.tick(CONFIG.FPS)

                with TIMERS["updates"]:
                    self.updates(dt)

                with TIMERS["collisions"]:
                    self.collisions()

            self.stats()


Game().main()


logger.info("Finished")
pg.quit()
sys.exit()
