from __future__ import annotations
import pygame as pg
import sys
from pygame.locals import *
from consts import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, BLACK, ALL_SHIFTS
from delayed import DelayedEvent, ALL_DELAYED

pg.init()
DISPLAYSURF = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pg.NOFRAME | pg.SRCALPHA | pg.SCALED,
)

from players import spawn_player, get_player
from enemies import spawn_asteroid
from collisions import ALL_SPRITES_CD
from groups import ALL_ASTEROIDS, ALL_SPRITES
from math_utils import collide_objects
from timers import TIMERS
from objects import MovingObject
from assets import BackgroundImage

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s.py %(funcName)s %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Started")

DISPLAYSURF.blit(BackgroundImage, (0, 0))
FramePerSec = pg.time.Clock()

font = pg.font.SysFont("Lucida Console", 60)
font_small = pg.font.SysFont("Lucida Console", 20)

pg.display.set_caption("NotTyrian")

SHOW_SPEEDS = False
SHOW_HP = True

with TIMERS["init"]:
    spawn_player(1)
    spawn_player(2)

    while len(ALL_ASTEROIDS) < 10:
        spawn_asteroid()

DelayedEvent(
    lambda: spawn_asteroid() if len(ALL_ASTEROIDS) < 50 else None,
    5000,
    repeat=True,
    name="spawn_asteroid",
)


def main():
    cnt = 0
    all_changes = []
    all_shift_sprites: dict(tuple(int, int), pg.sprite.RenderUpdates) = {
        (shift.x, shift.y): pg.sprite.RenderUpdates(*ALL_SPRITES)
        for shift in ALL_SHIFTS
    }

    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_BACKSPACE:
                    global SHOW_SPEEDS
                    SHOW_SPEEDS = not SHOW_SPEEDS
                elif event.key == K_EQUALS:
                    global SHOW_HP
                    SHOW_HP = not SHOW_HP

        for shift_sprites in all_shift_sprites.values():
            shift_sprites.add(ALL_SPRITES)

        with TIMERS["clears"]:
            for g in all_shift_sprites.values():
                g.clear(DISPLAYSURF, BackgroundImage)
        with TIMERS["blits"]:
            for change in all_changes:
                DISPLAYSURF.blit(BackgroundImage, change, change)

        all_changes = []

        with TIMERS["draw"]:
            for shift in ALL_SHIFTS:
                for sprite in ALL_SPRITES:
                    sprite.rect.move_ip(shift)
                all_shift_sprites[(shift.x, shift.y)].draw(DISPLAYSURF)
                for sprite in ALL_SPRITES:
                    sprite.rect.move_ip(-shift)

        with TIMERS["debugs"]:
            if SHOW_SPEEDS:
                sprite: MovingObject
                for sprite in ALL_SPRITES.sprites():
                    all_changes.extend(sprite.draw_debugs(DISPLAYSURF))

        with TIMERS["UX"]:
            if SHOW_HP:
                sprite: MovingObject
                for sprite in ALL_SPRITES.sprites():
                    all_changes.extend(sprite.draw_ui(DISPLAYSURF))

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)

        with TIMERS["blits"]:
            all_changes.append(DISPLAYSURF.blit(fps_render, (10, 10)))

        pg.display.flip()

        dt = FramePerSec.tick(FPS)
        with TIMERS["delayed events"]:
            ALL_DELAYED.update(dt)

        def on_collision(obj_a: MovingObject, obj_b: MovingObject):
            force = collide_objects(obj_a, obj_b)
            obj_a.on_collision(obj_b)
            obj_b.on_collision(obj_a)
            obj_a.apply_damage(force)
            obj_b.apply_damage(force)

        with TIMERS["collide"]:
            for sprite in ALL_SPRITES:
                ALL_SPRITES_CD.collide_with_callback(
                    sprite, on_collision=on_collision, stationary=False
                )

        with TIMERS["update"]:
            for sprite in ALL_SPRITES:
                sprite.update(dt)
        cnt += 1
        if cnt % 1000 == 0:
            logger.info(
                f"total:{sum(timer.val for timer in TIMERS.values()):.3f} "
                + " ".join(f"{k}:{v}" for k, v in TIMERS.items())
            )
            for t in TIMERS.values():
                t.reset()


main()
logger.info("Finished")
pg.quit()
sys.exit()
