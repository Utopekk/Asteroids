import pygame
import sys
import math
import time


# Constructor SpaceObject
class SpaceObject:
    def __init__(self, n_size, x, y, dx, dy, angle):
        self.n_size = n_size
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = angle
        self.creation_time = time.time()


# Constructor AsteroidsGame
class AsteroidsGame:
    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Asteroids")
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.vec_asteroids = [SpaceObject(n_size=40, x=0.0, y=0.0, dx=10.0, dy=10.0, angle=0.0)]
        self.player = SpaceObject(n_size=20.0, x=screen_width / 2.0, y=screen_height / 2.0, dx=0.0, dy=0.0, angle=0.0)
        self.vec_bullets = []
        self.interval_shooting = 1
        self.last_time_shot = 0

    # Handle input
    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.angle -= 1.2 * self.elapsed_time

        if keys[pygame.K_RIGHT]:
            self.player.angle += 1.2 * self.elapsed_time

        if keys[pygame.K_UP]:
            self.player.dx += math.sin(self.player.angle) * 20.0 * self.elapsed_time
            self.player.dy += -math.cos(self.player.angle) * 20.0 * self.elapsed_time

        now = int(time.time())
        if keys[pygame.K_SPACE] and (now - self.last_time_shot) >= self.interval_shooting:
            self.vec_bullets.append(SpaceObject(
                n_size=0,
                x=self.player.x,
                y=self.player.y,
                dx=50.0 * math.sin(self.player.angle),
                dy=-50.0 * math.cos(self.player.angle),
                angle=0.0
            ))
            self.last_time_shot = now

    # Update bullets and wrap objects
    def update_objects(self):
        self.vec_bullets = [b for b in self.vec_bullets if time.time() - b.creation_time <= 3]

        for obj in self.vec_asteroids + [self.player] + self.vec_bullets:
            obj.x += obj.dx * self.elapsed_time
            obj.y += obj.dy * self.elapsed_time
            obj.x, obj.y = self.wrap(obj.x, obj.y)

    # Drawing
    def draw_objects(self):
        # Draw square
        for obj in self.vec_asteroids:
            pygame.draw.rect(self.screen, self.white, (int(obj.x), int(obj.y), obj.n_size, obj.n_size))

        # Draw bullets
        for bullet in self.vec_bullets:
            bullet.x += bullet.dx * self.elapsed_time
            bullet.y += bullet.dy * self.elapsed_time
            bullet.x, bullet.y = self.wrap(bullet.x, bullet.y)
            pygame.draw.rect(self.screen, self.white, pygame.Rect(bullet.x, bullet.y, 5, 5))

        # Draw the player's ship as a triangle
        mx = [0.0, -20.0, 20.0]
        my = [-44.0, 20.0, 20.0]

        sx = []
        sy = []
        for i in range(3):
            sx.append(mx[i] * math.cos(self.player.angle) - my[i] * math.sin(self.player.angle))
            sy.append(mx[i] * math.sin(self.player.angle) + my[i] * math.cos(self.player.angle))

        for i in range(3):
            sx[i] = sx[i] + self.player.x
            sy[i] = sy[i] + self.player.y

        pygame.draw.polygon(self.screen, self.white, [(sx[0], sy[0]), (sx[1], sy[1]), (sx[2], sy[2])])

    # If you go outside the map you teleport to the other side
    def wrap(self, ix, iy):
        ox, oy = ix, iy
        if ix < 0.0:
            ox = ix + self.screen_width
        elif ix >= self.screen_width:
            ox = ix - self.screen_width
        if iy < 0.0:
            oy = iy + self.screen_height
        elif iy >= self.screen_height:
            oy = iy - self.screen_height
        return ox, oy

    # Main setup
    def run_game(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.elapsed_time = 0.1
            self.handle_input()
            self.update_objects()

            self.screen.fill(self.black)
            self.draw_objects()

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    game = AsteroidsGame(screen_width=1280, screen_height=720)
    game.run_game()
