from __future__ import annotations
import pygame
import sys
from pygame.locals import *

# import pygame.gfxdraw
from object import MovingObject, Player, Asteroid
from consts import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, BLACK, ALL_SHIFTS
from math_utils import collide_objects
import random
from timers import TIMERS
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS

pygame.init()
DISPLAYSURF = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pygame.NOFRAME | pygame.SRCALPHA | pygame.SCALED,
)

from assets import PlayerImages, AsteroidLargeImage, BackgroundImage

FramePerSec = pygame.time.Clock()

font = pygame.font.SysFont("Lucida Console", 60)
font_small = pygame.font.SysFont("Lucida Console", 20)

pygame.display.set_caption("NotTyrian")

SHOW_SPEEDS = True

all_players = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


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
    if not player1.any_collision_with_callbacks(all_sprites):
        all_players.add(player1)
        all_sprites.add(player1)
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
    if not player1.any_collision_with_callbacks(all_sprites):
        all_players.add(player2)
        all_sprites.add(player2)
        break

all_asteroids = pygame.sprite.Group()

while len(all_asteroids) < 20:
    asteroid = Asteroid(
        image=AsteroidLargeImage,
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
    if not asteroid.any_collision_with_callbacks(all_sprites):
        all_asteroids.add(asteroid)
        all_sprites.add(asteroid)

DISPLAYSURF.blit(BackgroundImage, (0, 0))
all_shift_sprites = {
    (shift.x, shift.y): pygame.sprite.RenderUpdates(*all_sprites)
    for shift in ALL_SHIFTS
}


def main():
    cnt = 0
    all_changes = []
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_BACKSPACE:
                global SHOW_SPEEDS
                SHOW_SPEEDS = not SHOW_SPEEDS

        with TIMERS["clears"]:
            for g in all_shift_sprites.values():
                g.clear(DISPLAYSURF, BackgroundImage)
        with TIMERS["blits"]:
            for change in all_changes:
                DISPLAYSURF.blit(BackgroundImage, change, change)

        all_changes = []

        with TIMERS["draw"]:
            for shift in ALL_SHIFTS:
                for sprite in all_sprites:
                    sprite.rect.move_ip(shift)
                all_shift_sprites[(shift.x, shift.y)].draw(DISPLAYSURF)
                for sprite in all_sprites:
                    sprite.rect.move_ip(-shift)

        with TIMERS["debugs"]:
            if SHOW_SPEEDS:
                for sprite in all_sprites.sprites():
                    assert isinstance(sprite, MovingObject)
                    all_changes.extend(sprite.draw_debugs(DISPLAYSURF))

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)

        with TIMERS["blits"]:
            all_changes.append(DISPLAYSURF.blit(fps_render, (10, 10)))

        pygame.display.flip()

        dt = FramePerSec.tick(FPS)

        with TIMERS["collide"]:
            processed_sprites = pygame.sprite.Group()
            for sprite in all_sprites:
                assert isinstance(sprite, MovingObject)

                def _on_collision(_sprite, _col):
                    collide_objects(_sprite, _col)
                    processed_sprites.remove(_col)

                if not sprite.any_collision_with_callbacks(
                    processed_sprites, _on_collision
                ):
                    processed_sprites.add(sprite)
        with TIMERS["update"]:
            all_sprites.update(dt)
        cnt += 1
        if cnt % 1000 == 0:
            print(dict(TIMERS))
            for t in TIMERS.values():
                t.reset()


main()
pygame.quit()
sys.exit()
