import pygame
import sys

class SpaceObject:
    def __init__(self, n_size, x, y, dx, dy):
        self.n_size = n_size
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy


pygame.init()
ScreenWidth = 1280
ScreenHeight = 720
screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
pygame.display.set_caption("Asteroids")
white = (255, 255, 255)
black = (0, 0, 0)

vec_asteroids = [SpaceObject(n_size=30, x=0.0, y=0.0, dx=10.0, dy=10.0)]


def on_user_update(f_elapsed_time):
    for a in vec_asteroids:
        a.x += a.dx * f_elapsed_time
        a.y += a.dy * f_elapsed_time
        a.x, a.y = Wrap(a.x, a.y)
        pygame.draw.rect(screen, white, (int(a.x), int(a.y), a.n_size, a.n_size))


def Wrap(ix, iy):
    ox, oy = ix, iy
    if ix < 0.0:
        ox = ix + ScreenWidth
    elif ix >= ScreenWidth:
        ox = ix - ScreenWidth
    if iy < 0.0:
        oy = iy + ScreenHeight
    elif iy >= ScreenHeight:
        oy = iy - ScreenHeight
    return ox, oy


# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(black)
    on_user_update(0.1)

    pygame.display.flip()
    clock.tick(60)
