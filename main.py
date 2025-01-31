import pygame, sys
import pygame.transform
import numpy as np
from pygame.locals import *
import math
import random
from timeit import default_timer as timer

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

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)



DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.NOFRAME | pygame.SRCALPHA | pygame.SCALED)
pygame.display.set_caption("NotTyrian")

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

class Object(pygame.sprite.Sprite):
    rect: pygame.Rect
    image: pygame.Surface

    def blit_to_surface(self, target: pygame.Surface):
        size_x = target.get_width()
        size_y = target.get_height()

        if not target.get_rect().contains(self.rect):
            for a in [-1,0,1]:
                for b in [-1,0,1]:
                    target.blit(self.image, self.rect.move(a * size_x, b * size_y))
        else:
            target.blit(self.image, self.rect)

class MovingObject(Object):
    FORWARD_THRUST = 0.1 / 1000
    SIDE_THRUST = FORWARD_THRUST
    ANGULAR_THRUST = 0.2 / 1000
    MAX_ANGULAR_SPEED = 0.3
    MAX_FORWARD_SPEED = 0.3
    DRAG = FORWARD_THRUST / MAX_FORWARD_SPEED ** 2
    ANGULAR_DRAG = ANGULAR_THRUST / MAX_ANGULAR_SPEED ** 2

    def __init__(self, image, init_pos, init_speed):
        super().__init__()

        self._image = image

        self.pos = np.array([init_pos[0]%SCREEN_WIDTH, init_pos[1]%SCREEN_HEIGHT, init_pos[2]%360])
        self.speed = np.array(init_speed)

        self.update_image_rect()
        self._acc = (0.0, 0.0)
        self._drag = (0.0, 0.0)

    def blit_to_surface(self, target: pygame.Surface):
        super().blit_to_surface(target)
        if SHOW_SPEEDS:
            dt = 200
            pygame.draw.line(target,
                             WHITE,
                             (self.pos[0], self.pos[1]),
                             (self.pos[0]+dt*self.speed[0], self.pos[1]+dt*self.speed[1]),
                             1
                            )
            dt = 200000
            pygame.draw.line(target,
                             GREEN,
                             (self.pos[0], self.pos[1]),
                             (self.pos[0]+dt*self._acc[0], self.pos[1]+dt*self._acc[1]),
                             1
                            )
            pygame.draw.line(target,
                             RED,
                             (self.pos[0]+dt*self._acc[0], self.pos[1]+dt*self._acc[1]),
                             (self.pos[0]+dt*self._acc[0]-dt*self._drag[0], self.pos[1]+dt*self._acc[1]-dt*self._drag[1]),
                             1
                            )

    def update_image_rect(self):
        #self.image = self.images[round((self.NUM_OF_ROTATIONS*(self.pos[2]%360))//360)]
        self.image = pygame.transform.rotate(self._image, self.pos[2]%360)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos[0]%SCREEN_WIDTH, self.pos[1]%SCREEN_HEIGHT)

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
            self._acc = (acc[0], acc[1])
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
            self._drag = (drag_x, drag_y)
            return np.concatenate([speed, acc])

        new_pos_speed = range_kutta_4(F, np.concatenate([self.pos, self.speed]), dt)


        self.pos = new_pos_speed[0:3]
        self.speed = new_pos_speed[3:6]

        self.pos[0] %= SCREEN_WIDTH
        self.pos[1] %= SCREEN_HEIGHT
        self.pos[2] %= 360


class Player(MovingObject):
    def get_accels(self) -> tuple[float, float, float]:
        pressed_keys = pygame.key.get_pressed()

        forward_accel = self.FORWARD_THRUST * (int(pressed_keys[K_w]) - int(pressed_keys[K_s]))
        angular_accel = self.ANGULAR_THRUST * (int(pressed_keys[K_a]) - int(pressed_keys[K_d]))
        side_accel = self.SIDE_THRUST * (int(pressed_keys[K_q]) - int(pressed_keys[K_e]))

        return forward_accel, angular_accel, side_accel

class Asteroid(MovingObject):
    def get_accels(self):
        return 0.0, 0.0, 0.0

player = Player(
    load_from_file(48, 112, 24, 27,"assets/tyrian/tyrian.shp.007D3C.png"),
    [SCREEN_WIDTH/2,SCREEN_HEIGHT/2,0],
    [0,0,0]
)

asteroid = Asteroid(
    load_from_file(0, 0, 45, 48, "assets/tyrian/newshd.shp.000000.png"),
    [random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),random.randint(0, 360)],
    [random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)]
)


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
        player.blit_to_surface(DISPLAYSURF)
        asteroid.blit_to_surface(DISPLAYSURF)

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)
        DISPLAYSURF.blit(fps_render, (10, 10))

        pygame.display.update()
        dt = FramePerSec.tick(FPS)
        player.update(dt)
        asteroid.update(dt)

main()
pygame.quit()
sys.exit()



