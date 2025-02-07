from __future__ import annotations
import pygame
import sys
from pygame.locals import *
from consts import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, BLACK, ALL_SHIFTS

pygame.init()
DISPLAYSURF = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pygame.NOFRAME | pygame.SRCALPHA | pygame.SCALED,
)

from players import Player
from collisions import CollisionDetector
from groups import ALL_ASTEROIDS, ALL_SPRITES
from math_utils import collide_objects
import random
from timers import TIMERS
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS
from objects import MovingObject, Asteroid
from assets import PlayerImages, BackgroundImage

DISPLAYSURF.blit(BackgroundImage, (0, 0))
FramePerSec = pygame.time.Clock()

font = pygame.font.SysFont("Lucida Console", 60)
font_small = pygame.font.SysFont("Lucida Console", 20)

pygame.display.set_caption("NotTyrian")

SHOW_SPEEDS = True


while True:
    player1 = Player(
        controls=PLAYER_1_CONTROLS,
        image=PlayerImages[2],
        init_pos=(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            random.randint(0, 360),
        ),
        init_speed=(0, 0, 0),
    )
    if CollisionDetector(*ALL_SPRITES).collide_with_callback(player1, stationary=True):
        player1.kill()
    else:
        break


while True:
    player2 = Player(
        controls=PLAYER_2_CONTROLS,
        image=PlayerImages[1],
        init_pos=(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            random.randint(0, 360),
        ),
        init_speed=(0, 0, 0),
    )
    if CollisionDetector(*ALL_SPRITES).collide_with_callback(player2, stationary=True):
        player2.kill()
    else:
        break

cd = CollisionDetector(*ALL_SPRITES)
while len(ALL_ASTEROIDS) < 20:
    asteroid = Asteroid(
        init_pos=[
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            random.randint(0, 360),
        ],
        init_speed=[
            random.uniform(-0.1, 0.1),
            random.uniform(-0.1, 0.1),
            random.uniform(-0.1, 0.1),
        ],
    )
    if cd.collide_with_callback(asteroid, stationary=True):
        asteroid.kill()
    else:
        cd.add(asteroid)
del cd


def main():
    cnt = 0
    all_changes = []
    all_shift_sprites: dict(tuple(int, int), pygame.sprite.RenderUpdates) = {
        (shift.x, shift.y): pygame.sprite.RenderUpdates(*ALL_SPRITES)
        for shift in ALL_SHIFTS
    }

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_BACKSPACE:
                global SHOW_SPEEDS
                SHOW_SPEEDS = not SHOW_SPEEDS

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
                for sprite in ALL_SPRITES.sprites():
                    assert isinstance(sprite, MovingObject)
                    all_changes.extend(sprite.draw_debugs(DISPLAYSURF))

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)

        with TIMERS["blits"]:
            all_changes.append(DISPLAYSURF.blit(fps_render, (10, 10)))

        pygame.display.flip()

        dt = FramePerSec.tick(FPS)

        with TIMERS["collide"]:
            cd = CollisionDetector(*ALL_SPRITES)
            for sprite in ALL_SPRITES:
                cd.collide_with_callback(
                    sprite, on_collision=collide_objects, stationary=False
                )

        with TIMERS["update"]:
            for sprite in ALL_SPRITES:
                sprite.update(dt)
        cnt += 1
        if cnt % 1000 == 0:
            print(dict(TIMERS))
            for t in TIMERS.values():
                t.reset()


main()
pygame.quit()
sys.exit()
