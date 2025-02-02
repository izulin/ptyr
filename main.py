from __future__ import annotations
import pygame, sys
from pygame.locals import *

# import pygame.gfxdraw
from sprite import MovingObject, Player, Asteroid
from consts import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, BLACK
from math_utils import test_if_proper_collision, collide_objects
import random

pygame.init()
FramePerSec = pygame.time.Clock()

font = pygame.font.SysFont("Lucida Console", 60)
font_small = pygame.font.SysFont("Lucida Console", 20)

DISPLAYSURF = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pygame.NOFRAME | pygame.SRCALPHA | pygame.SCALED,
)
pygame.display.set_caption("NotTyrian")

NUM_SCENES = 2
ALL_SCENES = [
    pygame.Surface((3 * SCREEN_WIDTH, 3 * SCREEN_HEIGHT), flags=pygame.SRCALPHA)
    for _ in range(NUM_SCENES)
]
[OBJECT_SCENE, UX_SCENE] = ALL_SCENES

background_image = pygame.image.load("assets/background.jpg").convert_alpha()
BACKGROUND = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
SHOW_SPEEDS = False

from assets import PlayerImages, AsteroidImage
from controls import PLAYER_1_CONTROLS, PLAYER_2_CONTROLS

all_players = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

for num_of_player in range(2):
    player = Player(
        controls=[PLAYER_1_CONTROLS, PLAYER_2_CONTROLS][num_of_player],
        image=[PlayerImages[2], PlayerImages[1]][num_of_player],
        init_pos=[
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            random.randint(0, 360),
        ],
        init_speed=[0, 0, 0],
    )
    all_players.add(player)
    all_sprites.add(player)

all_asteroids = pygame.sprite.Group()

while len(all_asteroids) < 10:
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
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_BACKSPACE:
                global SHOW_SPEEDS
                SHOW_SPEEDS = not SHOW_SPEEDS

        DISPLAYSURF.blit(BACKGROUND, (0, 0))
        for scene in ALL_SCENES:
            scene.fill((0, 0, 0, 0))

        all_sprites.draw(OBJECT_SCENE)
        if SHOW_SPEEDS:
            for sprite in all_sprites.sprites():
                assert isinstance(sprite, MovingObject)
                sprite.draw_debugs(UX_SCENE)

        for scene in ALL_SCENES:
            for a in range(0, 3):
                for b in range(0, 3):
                    DISPLAYSURF.blit(
                        scene,
                        (0, 0),
                        (
                            SCREEN_WIDTH * a,
                            SCREEN_HEIGHT * b,
                            SCREEN_WIDTH,
                            SCREEN_HEIGHT,
                        ),
                    )

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)

        DISPLAYSURF.blit(fps_render, (10, 10))
        pygame.display.flip()
        dt = FramePerSec.tick(FPS)
        processed_sprites = pygame.sprite.Group()
        for sprite in all_sprites:
            assert isinstance(sprite, MovingObject)
            collision = pygame.sprite.spritecollideany(
                sprite, processed_sprites, pygame.sprite.collide_mask
            )
            if collision is None or not test_if_proper_collision(sprite, collision):
                processed_sprites.add(sprite)
                continue
            else:
                collide_objects(sprite, collision)
                processed_sprites.remove(collision)

        all_sprites.update(dt)


main()
pygame.quit()
sys.exit()
