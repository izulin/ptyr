from __future__ import annotations
import pygame, sys
from pygame.locals import *

# import pygame.gfxdraw
from sprite import MovingObject, Player, Asteroid
from consts import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, BLACK, ALL_SHIFTS
from math_utils import test_if_proper_collision, collide_objects
import random
from timers import TIMERS
from pygame.math import Vector3


pygame.init()
FramePerSec = pygame.time.Clock()

font = pygame.font.SysFont("Lucida Console", 60)
font_small = pygame.font.SysFont("Lucida Console", 20)

DISPLAYSURF = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pygame.NOFRAME | pygame.SRCALPHA | pygame.SCALED,
)
pygame.display.set_caption("NotTyrian")


SHOW_SPEEDS = False

from assets import PlayerImages, AsteroidImage, BackgroundImage
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS

all_players = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


for num_of_player in range(2):
    player = Player(
        controls=[PLAYER_1_CONTROLS, PLAYER_2_CONTROLS][num_of_player],
        image=[PlayerImages[2], PlayerImages[1]][num_of_player],
        init_pos=(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            random.randint(0, 360),
        ),
        init_speed=(0, 0, 0),
    )
    all_players.add(player)
    all_sprites.add(player)

all_asteroids = pygame.sprite.Group()

while len(all_asteroids) < 40:
    asteroid = Asteroid(
        image=AsteroidImage,
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
    collision = pygame.sprite.spritecollideany(
        asteroid, all_sprites, pygame.sprite.collide_mask
    )
    if collision is None:
        all_sprites.add(asteroid)
        all_asteroids.add(asteroid)


def main():
    cnt = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_BACKSPACE:
                global SHOW_SPEEDS
                SHOW_SPEEDS = not SHOW_SPEEDS

        with TIMERS["blits"]:
            DISPLAYSURF.blit(BackgroundImage, (0, 0))

        with TIMERS["draw"]:
            for shift in ALL_SHIFTS:
                for sprite in all_sprites:
                    sprite.rect.move_ip(shift)
                all_sprites.draw(DISPLAYSURF)
                for sprite in all_sprites:
                    sprite.rect.move_ip(-shift)

        with TIMERS["debugs"]:
            if SHOW_SPEEDS:
                for sprite in all_sprites.sprites():
                    assert isinstance(sprite, MovingObject)
                    sprite.draw_debugs(DISPLAYSURF)

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)

        with TIMERS["blits"]:
            DISPLAYSURF.blit(fps_render, (10, 10))
        pygame.display.flip()
        dt = FramePerSec.tick(FPS)

        with TIMERS["collide"]:
            processed_sprites = pygame.sprite.Group()
            for sprite in all_sprites:
                assert isinstance(sprite, MovingObject)
                for shift in ALL_SHIFTS:
                    sprite.pos += Vector3(shift.x, shift.y, 0)
                    sprite.rect.move_ip(shift)
                    col = pygame.sprite.spritecollideany(
                        sprite, processed_sprites, collide_rect_mask
                    )
                    if col is not None and test_if_proper_collision(sprite, col):
                        collide_objects(sprite, col)
                        processed_sprites.remove(col)
                        sprite.pos -= Vector3(shift.x, shift.y, 0)
                        sprite.rect.move_ip(-shift)
                        break
                    else:
                        sprite.pos -= Vector3(shift.x, shift.y, 0)
                        sprite.rect.move_ip(-shift)
                else:
                    processed_sprites.add(sprite)
        with TIMERS["update"]:
            all_sprites.update(dt)
        cnt += 1
        if cnt % 1000 == 0:
            print(dict(TIMERS))
            for t in TIMERS.values():
                t.reset()


def collide_rect_mask(a, b):
    return pygame.sprite.collide_rect(a, b) and pygame.sprite.collide_mask(a, b)


main()
pygame.quit()
sys.exit()
