from __future__ import annotations
import pygame as pg
import sys
from pygame.locals import *
from consts import FPS, BLACK, ALL_SHIFTS
from delayed import DelayedEvent, ALL_DELAYED
from typing import TYPE_CHECKING

pg.init()

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
    ALL_STATUSES,
    ALL_EXPLOSIONS,
)
from math_utils import collide_objects, get_collision_point
from timers import TIMERS

from assets import BackgroundImage

if TYPE_CHECKING:
    from powerups import PowerUp
    from objects import MovingObject
    from players import Player
    from explosions import Explosion

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

    while len(ALL_ENEMIES) < 3:
        spawn_asteroid()

DelayedEvent(
    lambda: spawn_asteroid() if len(ALL_ENEMIES) < 50 else None,
    5000,
    repeat=True,
    name="spawn_asteroid",
)


def _colliding_colliding(obj_a: MovingObject, obj_b: MovingObject):
    if id(obj_b) < id(obj_a):
        return
    obj_a.on_collision(obj_b)
    obj_b.on_collision(obj_a)
    collision_point = get_collision_point(obj_a, obj_b)
    energy = collide_objects(obj_a, obj_b, collision_point)
    obj_a.apply_damage(10 * energy)
    obj_b.apply_damage(10 * energy)


def _player_powerup(player: Player, powerup: PowerUp):
    powerup.on_collision(player)


def _explosion_colliding(explosion: Explosion, obj: MovingObject):
    explosion.on_collision(obj)


def main():
    cnt = 0
    all_shift_sprites: dict(tuple(int, int), pg.sprite.RenderUpdates) = {
        (shift.x, shift.y): pg.sprite.RenderUpdates(*ALL_DRAWABLE_OBJECTS)
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
            shift_sprites.add(ALL_DRAWABLE_OBJECTS)

        with TIMERS["clears"]:
            for g in all_shift_sprites.values():
                g.clear(DISPLAYSURF, BackgroundImage)
        with TIMERS["blits"]:
            for change in ALL_CHANGES_DISPLAYSURF:
                DISPLAYSURF.blit(BackgroundImage, change, change)

        ALL_CHANGES_DISPLAYSURF.clear()

        with TIMERS["draw"]:
            for shift in ALL_SHIFTS:
                for sprite in ALL_DRAWABLE_OBJECTS:
                    sprite.rect.move_ip(shift)
                all_shift_sprites[(shift.x, shift.y)].draw(DISPLAYSURF)
                for sprite in ALL_DRAWABLE_OBJECTS:
                    sprite.rect.move_ip(-shift)

        with TIMERS["debugs"]:
            if SHOW_SPEEDS:
                sprite: MovingObject
                for sprite in ALL_DRAWABLE_OBJECTS.sprites():
                    sprite.draw_debugs()

        with TIMERS["UX"]:
            if SHOW_HP:
                sprite: MovingObject
                for sprite in ALL_UI_DRAWABLE_OBJECTS.sprites():
                    sprite.draw_ui()

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)

        with TIMERS["blits"]:
            ALL_CHANGES_DISPLAYSURF.append(DISPLAYSURF.blit(fps_render, (10, 10)))

        pg.display.flip()

        dt = FramePerSec.tick(FPS)

        with TIMERS["update"]:
            ALL_DELAYED.update(dt)
            ALL_STATUSES.update(dt)
            ALL_DRAWABLE_OBJECTS.update(dt)
            for sprite in ALL_DRAWABLE_OBJECTS:
                if not sprite.alive:
                    sprite.on_death()
                    sprite.kill()

        with TIMERS["collide"]:
            for sprite in ALL_COLLIDING_OBJECTS:
                ALL_COLLIDING_OBJECTS.cd.collide_with_callback(
                    sprite, on_collision=_colliding_colliding, stationary=False
                )
            for player in ALL_PLAYERS:
                ALL_POWERUPS.cd.collide_with_callback(
                    player, on_collision=_player_powerup, stationary=True
                )

            for explosion in ALL_EXPLOSIONS:
                ALL_COLLIDING_OBJECTS.cd.collide_with_callback(
                    explosion, on_collision=_explosion_colliding, stationary=True
                )

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
