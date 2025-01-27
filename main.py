import pygame, sys
import pygame.transform
import numpy as np
from pygame.locals import *

pygame.init()
FPS = 120
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
background = pygame.transform.scale(background_image,(SCREEN_WIDTH, SCREEN_HEIGHT))

def load_from_file(posx: int, posy: int, sizex: int, sizey: int, filename: str):
    ret_surface = pygame.Surface((sizex, sizey), flags=pygame.SRCALPHA)
    image = pygame.image.load(filename).convert_alpha()
    ret_surface.blit(image, (0,0), (posx, posy, sizex,sizey))
    return ret_surface

def remove_background(surface):
    pxarray = pygame.PixelArray(surface)
    pxarray.replace((191, 220, 191, 255), (0, 0, 0, 0), 0.1)

class SpriteWithPosition(pygame.sprite.Sprite):
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

class Player(SpriteWithPosition):
    def __init__(self):
        super().__init__()
        image = load_from_file(48, 112, 24, 27,"assets/tyrian/tyrian.shp.007D3C.png")
        remove_background(image)

        self.images = [pygame.transform.rotate(image, 360*i/100) for i in range(100)]

        self.pos = np.array([SCREEN_WIDTH/2,SCREEN_HEIGHT/2,0]) #x,y,angular
        self.speed = np.array([0.0,0.0,0.0])

        self.update_image_rect()

    def update_image_rect(self):
        self.image = self.images[round((100*self.pos[2])//360)]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos[0], self.pos[1])

    def update_pos(self, dt: float):
        pressed_keys = pygame.key.get_pressed()



        FORWARD_ACC_RATE = 0.1
        SIDE_ACC_RATE = 0.1
        ANGULAR_ACC_RATE = 0.1

        forward_acc = 0.0
        angular_acc = 0.0
        side_acc = 0.0

        if pressed_keys[K_w]:
            forward_acc += FORWARD_ACC_RATE
        if pressed_keys[K_s]:
            forward_acc -= FORWARD_ACC_RATE
        if pressed_keys[K_a]:
            angular_acc += ANGULAR_ACC_RATE
        if pressed_keys[K_d]:
            angular_acc -= ANGULAR_ACC_RATE
        if pressed_keys[K_q]:
            side_acc += SIDE_ACC_RATE
        if pressed_keys[K_e]:
            side_acc -= SIDE_ACC_RATE


        radians = (270-self.pos[2])/360*2*np.pi
        acc = np.array([forward_acc*np.cos(radians)+side_acc*np.sin(radians),forward_acc*np.sin(radians)-side_acc*np.cos(radians),angular_acc])
        self.speed += acc * dt * 0.001
        MAX_ANGULAR_SPEED = 0.5
        self.speed[2] = max(min(self.speed[2],MAX_ANGULAR_SPEED),-MAX_ANGULAR_SPEED)
        MAX_FORWARD_SPEED = 0.1
        if (tmp:=(self.speed[0]**2 + self.speed[1]**2)) > MAX_FORWARD_SPEED**2:
            tmp = np.sqrt(tmp)/MAX_FORWARD_SPEED
            self.speed[0] /= tmp
            self.speed[1] /= tmp

        if pressed_keys[K_SPACE]:
            self.speed = np.array([0.0,0.0,0.0])

        self.pos += self.speed * dt

        self.pos[0] %= SCREEN_WIDTH
        self.pos[1] %= SCREEN_HEIGHT
        self.pos[2] %= 360

        self.update_image_rect()



player = Player()

def main():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return


        DISPLAYSURF.blit(background, (0, 0))
        player.blit_to_surface(DISPLAYSURF)

        fps = FramePerSec.get_fps()
        fps_render = font_small.render(f"{fps:.2f}.", True, BLACK)
        DISPLAYSURF.blit(fps_render, (10, 10))

        pygame.display.update()
        dt = FramePerSec.tick(FPS)
        player.update_pos(dt)

main()
pygame.quit()
sys.exit()



