import pygame
import sys
import math


class SpaceObject:
    def __init__(self, n_size, x, y, dx, dy, angle):
        self.n_size = n_size
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = angle


pygame.init()
ScreenWidth = 1280
ScreenHeight = 720
screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
pygame.display.set_caption("Asteroids")
white = (255, 255, 255)
black = (0, 0, 0)

vec_asteroids = [SpaceObject(n_size=40, x=0.0, y=0.0, dx=10.0, dy=10.0, angle=0.0)]
player = SpaceObject(n_size=20, x=20.0, y=20.0, dx=20.0, dy=20.0, angle=0.0)
vec_bullets = []
player.x = ScreenWidth / 2.0
player.y = ScreenHeight / 2.0
player.dx = 0.0
player.dy = 0.0
player.angle = 0.0
player.n_size = 0.0


def on_user_update(f_elapsed_time):
    for a in vec_asteroids:
        a.x += a.dx * f_elapsed_time
        a.y += a.dy * f_elapsed_time
        a.x, a.y = Wrap(a.x, a.y)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.angle -= 5.0 * f_elapsed_time

        if keys[pygame.K_RIGHT]:
            player.angle += 5.0 * f_elapsed_time

        if keys[pygame.K_UP]:
            player.dx += math.sin(player.angle) * 20.0 * f_elapsed_time
            player.dy += -math.cos(player.angle) * 20.0 * f_elapsed_time

        if keys[pygame.K_SPACE]:
            vec_bullets.append(SpaceObject(n_size=0, x=player.x, y=player.y, dx=50.0 * math.sin(player.angle),
                                           dy=-50.0 * math.cos(player.angle), angle=0.0))

        player.x += player.dx * f_elapsed_time
        player.y += player.dy * f_elapsed_time

        player.x, player.y = Wrap(player.x, player.y)

        pygame.draw.rect(screen, white, (int(a.x), int(a.y), a.n_size, a.n_size))

        mx = [0.0, -20.0, 20.0]
        my = [-44.0, 20.0, 20.0]

        sx = []
        sy = []
        for i in range(3):
            sx.append(mx[i] * math.cos(player.angle) - my[i] * math.sin(player.angle))
            sy.append(mx[i] * math.sin(player.angle) + my[i] * math.cos(player.angle))

        for i in range(3):
            sx[i] = sx[i] + player.x
            sy[i] = sy[i] + player.y

        for i in range(4):
            j = i + 1
            pygame.draw.line(screen, white, ([sx[i % 3], sy[i % 3]]), ([sx[j % 3], sy[j % 3]]))

    for b in vec_bullets:
        b.x += b.dx * f_elapsed_time
        b.y += b.dy * f_elapsed_time
        b.x, b.y = Wrap(b.x, b.y)
        pygame.draw.line(screen, white, (b.x, b.y), (b.x, b.y), width=4)


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
