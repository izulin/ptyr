from __future__ import annotations
import pygame, sys
import pygame.transform
import numpy as np
from pygame.locals import *
#import pygame.gfxdraw
import math
import random

pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

font = pygame.font.SysFont("Lucida Console", 60)
font_small = pygame.font.SysFont("Lucida Console", 20)



DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.NOFRAME | pygame.SRCALPHA | pygame.SCALED)
pygame.display.set_caption("NotTyrian")

NUM_SCENES = 2
ALL_SCENES = [pygame.Surface((3*SCREEN_WIDTH, 3*SCREEN_HEIGHT),flags = pygame.SRCALPHA) for _ in range(NUM_SCENES)]
[OBJECT_SCENE, UX_SCENE] = ALL_SCENES

background_image = pygame.image.load("assets/background.jpg").convert_alpha()
BACKGROUND = pygame.transform.scale(background_image,(SCREEN_WIDTH, SCREEN_HEIGHT))
SHOW_SPEEDS = False

def sgn(x: float):
    if x>0:
        return 1
    elif x<0:
        return -1
    else:
        return 0

def range_kutta_4(f, y, dt):
    k1 = f(y)
    k2 = f(y + dt / 2 * k1)
    k3 = f(y + dt / 2 * k2)
    k4 = f(y + dt * k3)

    return y + (k1 + 2 * k2 + 2 * k3 + k4) * dt / 6

def range_kutta_1(f, y, dt):
    return y + f(y) * dt

def load_from_file(posx: int, posy: int, sizex: int, sizey: int, filename: str):
    ret_surface = pygame.Surface((sizex, sizey), flags=pygame.SRCALPHA)
    image = pygame.image.load(filename).convert_alpha()
    ret_surface.blit(image, (0,0), (posx, posy, sizex,sizey))
    return remove_background(ret_surface)

def remove_background(surface):
    """In place removal."""
    pxarray = pygame.PixelArray(surface)
    pxarray.replace((191, 220, 191, 255), (0, 0, 0, 0), 0.001)
    return surface

def normalize_pos(pos):
    (posx, posy) = pos
    return (posx % SCREEN_WIDTH + SCREEN_WIDTH, posy % SCREEN_HEIGHT + SCREEN_HEIGHT)

class MovingObject(pygame.sprite.Sprite):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = FORWARD_THRUST
    ANGULAR_THRUST = 0.2 / 1000
    DRAG = 1 / 1000
    ANGULAR_DRAG = ANGULAR_THRUST / 0.3 ** 2

    def __init__(self, *, image, init_pos, init_speed, **kwargs):
        super().__init__(**kwargs)

        self._image = image

        self.pos = np.array([*normalize_pos(init_pos[:2]), init_pos[2]%360])
        self.speed = np.array(init_speed)

        self.update_image_rect()
        self._acc = np.array((0.0, 0.0))
        self._drag = np.array((0.0, 0.0))

    def draw_debugs(self, target: pygame.Surface):
        if SHOW_SPEEDS:
            dt = 200
            pygame.draw.line(target,
                             WHITE,
                             self.pos[:2],
                             self.pos[:2]+dt*self.speed[:2],
                             1
                            )
            dt = 200000
            pygame.draw.line(target,
                             GREEN,
                             self.pos[:2],
                             self.pos[:2]+dt*self._acc,
                             1
                            )
            pygame.draw.line(target,
                             RED,
                             self.pos[:2] + dt*self._acc,
                             self.pos[:2] + + dt*self._acc - dt * self._drag,
                             1
                            )

    def update_image_rect(self):
        self.image = pygame.transform.rotate(self._image, self.pos[2]%360)
        self.rect = self.image.get_rect()
        self.rect.center = normalize_pos(self.pos[:2])

    def update(self, dt: float):
        self.update_pos(dt)
        self.update_image_rect()

    def get_accels(self):
        raise NotImplementedError

    def update_pos(self, dt: float):
        forward_accel, angular_accel, side_accel = self.get_accels()

        def F(pos_speed):
            pos = pos_speed[0:3]
            speed = pos_speed[3:6]

            radians = (270-pos[2])/360*2*np.pi
            cosr = math.cos(radians)
            sinr = math.sin(radians)
            acc = np.array(
                [
                    forward_accel*cosr+side_accel*sinr,
                    forward_accel*sinr-side_accel*cosr,
                    angular_accel - (speed[2]**2)*sgn(speed[2]) * self.ANGULAR_DRAG
                ]
            )
            self._acc = np.array((acc[0], acc[1]))
            speed_squared = speed[0]**2+speed[1]**2
            drag_x = 0.0
            drag_y = 0.0
            if speed_squared > 0:
                drag_abs = speed_squared*self.DRAG
                speed_abs = math.sqrt(speed_squared)
                drag_x = drag_abs * speed[0] / speed_abs
                drag_y = drag_abs * speed[1] / speed_abs
            acc[0] -= drag_x
            acc[1] -= drag_y
            self._drag = np.array((drag_x, drag_y))
            return np.concatenate([speed, acc])

        new_pos_speed = range_kutta_4(F, np.concatenate([self.pos, self.speed]), dt)


        self.pos = new_pos_speed[0:3]
        self.speed = new_pos_speed[3:6]

        self.pos = np.array((*normalize_pos(self.pos[:2]), self.pos[2]%360))

def test_if_proper_collision(a: MovingObject, b: MovingObject):
    pos_diff = a.pos[:2] - b.pos[:2]
    speed_diff = a.speed[:2] - b.speed[:2]
    return pos_diff[0]*speed_diff[0] + pos_diff[1]*speed_diff[1] < 0

def collide_objects(a: MovingObject, b: MovingObject):
    pos_diff = a.pos[:2] - b.pos[:2]
    center_mass_speed = (a.speed[:2]*a.mass + b.speed[:2]*b.mass)/(a.mass+b.mass)
    a_speed_norm = a.speed[:2] - center_mass_speed
    b_speed_norm = b.speed[:2] - center_mass_speed
    a_proj = (a_speed_norm[0] * pos_diff[0] + a_speed_norm[1] * pos_diff[1]) / (pos_diff[0]**2 + pos_diff[1]**2) * pos_diff
    b_proj = (b_speed_norm[0] * pos_diff[0] + b_speed_norm[1] * pos_diff[1]) / (pos_diff[0]**2 + pos_diff[1]**2) * pos_diff
    ELASTICITY = 1.0
    a.speed[:2] -= (1.0+ELASTICITY)*a_proj
    b.speed[:2] -= (1.0+ELASTICITY)*b_proj


class Player(MovingObject):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = 0.05 / 1000
    ANGULAR_THRUST = 0.2 / 1000
    def get_accels(self) -> tuple[float, float, float]:
        pressed_keys = pygame.key.get_pressed()

        forward_accel = self.FORWARD_THRUST * (int(pressed_keys[K_w]) - int(pressed_keys[K_s]))
        angular_accel = self.ANGULAR_THRUST * (int(pressed_keys[K_a]) - int(pressed_keys[K_d]))
        side_accel = self.SIDE_THRUST * (int(pressed_keys[K_q]) - int(pressed_keys[K_e]))

        return forward_accel, angular_accel, side_accel

    @property
    def mass(self):
        return 30.0

class Asteroid(MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0
    mass = 100.0
    def get_accels(self):
        return 0.0, 0.0, 0.0

player = Player(
    image = load_from_file(48, 112, 24, 27,"assets/tyrian/tyrian.shp.007D3C.png"),
    init_pos = [SCREEN_WIDTH/2,SCREEN_HEIGHT/2,0],
    init_speed = [0,0,0]
)

all_sprites = pygame.sprite.Group(player)
all_asteroids = pygame.sprite.Group()

while len(all_asteroids) < 10:
    asteroid = Asteroid(
        image = load_from_file(0, 0, 45, 48, "assets/tyrian/newshd.shp.000000.png"),
        init_pos = [random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),random.randint(0, 360)],
        init_speed = [random.uniform(-0.1,0.1), random.uniform(-0.1,0.1), random.uniform(-0.1,0.1)]
    )
    collision = pygame.sprite.spritecollideany(asteroid, all_sprites, pygame.sprite.collide_mask)
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
            scene.fill((0,0,0,0))

        all_sprites.draw(OBJECT_SCENE)
        for sprite in all_sprites.sprites():
            assert isinstance(sprite, MovingObject)
            sprite.draw_debugs(UX_SCENE)

        for scene in ALL_SCENES:
            for a in range(0,3):
                for b in range(0,3):
                    DISPLAYSURF.blit(scene, (0,0), (SCREEN_WIDTH*a, SCREEN_HEIGHT*b, SCREEN_WIDTH, SCREEN_HEIGHT))

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)



        DISPLAYSURF.blit(fps_render, (10, 10))
        pygame.display.flip()
        dt = FramePerSec.tick(FPS)
        processed_sprites = pygame.sprite.Group()
        for sprite in all_sprites:
            assert isinstance(sprite, MovingObject)
            collision = pygame.sprite.spritecollideany(sprite, processed_sprites, pygame.sprite.collide_mask)
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



