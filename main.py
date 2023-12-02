import pygame
import sys
import math
import time
import random


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
class Player (SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle):
        super().__init__(n_size, x, y, dx, dy, angle)   
        self.acceleration = 0.1 
        self.speed = 10     
class Asteroid (SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle):
        super().__init__(n_size, x, y, dx, dy, angle)        
class Bullet (SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, acceleration):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = acceleration

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
        self.vec_asteroids = [Asteroid(n_size=40, x=0.0, y=0.0, dx=10.0, dy=10.0, angle=0.0)]
        self.player = Player(n_size=20.0, x=screen_width / 2.0, y=screen_height / 2.0, dx=0.0, dy=0.0, angle=0.0)
        self.vec_bullets = []
        self.interval_shooting = 1
        self.last_time_shot = 0
        self.counter_shooting = 0
        self.game_over = False
        self.game_over_time = 0

    # Handle input
    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.angle -= 1.2 * self.elapsed_time

        if keys[pygame.K_RIGHT]:
            self.player.angle += 1.2 * self.elapsed_time

        if keys[pygame.K_UP]:
            acceleration = 20.0 * self.player.acceleration
            self.player.dx += math.sin(self.player.angle) * acceleration
            self.player.dy += -math.cos(self.player.angle) * acceleration

            # Calculate the new speed
            self.player.speed = math.sqrt(self.player.dx**2 + self.player.dy**2)

        
            # Limit the speed
            max_speed = 140.0  # km/min
            if self.player.speed > max_speed:
                scale_factor = max_speed / self.player.speed
                self.player.dx *= scale_factor
                self.player.dy *= scale_factor
            # self.player_acceleration += 0.001 | better acceleration
        elif not (self.player.speed <= 10):
            damping_factor = 0.98
            self.player.dx *= damping_factor
            self.player.dy *= damping_factor
            self.player.speed = math.sqrt(self.player.dx**2 + self.player.dy**2)


        now = int(time.time())
        if keys[pygame.K_SPACE] and (now - self.last_time_shot) >= self.interval_shooting:
            acceleration = 1
            if(self.player.speed > 110):
                acceleration += self.player.speed * 0.01  
            self.vec_bullets.append(Bullet(
                n_size=0,
                x=self.player.x,
                y=self.player.y,
                dx=50.0 * math.sin(self.player.angle),
                dy=-50.0 * math.cos(self.player.angle),
                angle=0.0,
                acceleration=acceleration
            ))
            self.last_time_shot = now
            self.counter_shooting += 1

    # Update bullets and wrap objects
    def update_objects(self):
        self.vec_bullets = [b for b in self.vec_bullets if time.time() - b.creation_time <= 1.5]

        for obj in self.vec_asteroids + [self.player] + self.vec_bullets:
            obj.x += obj.dx * self.elapsed_time
            obj.y += obj.dy * self.elapsed_time
            obj.x, obj.y = self.wrap(obj.x, obj.y)

    # Drawing
    def draw_objects(self):
        # Draw circles instead of squares
        self.draw_circles()

        # Draw bullets
        for bullet in self.vec_bullets:

            bullet.x += bullet.dx * self.elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * self.elapsed_time * bullet.acceleration
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

    # Spawn asteroid
    def create_random_circles(self, num_circles):
        for _ in range(num_circles):
            size = random.randint(10, 30)  # Random size
            x = random.uniform(0, self.screen_width)  # Random x position
            y = random.uniform(0, self.screen_height)  # Random y position

            self.vec_asteroids.append(Asteroid(
                n_size=size,
                x=x,
                y=y,
                dx=random.uniform(-10, 10),  # Random speed in x direction
                dy=random.uniform(-10, 10),  # Random speed in y direction
                angle=random.uniform(0, 2 * math.pi)  # Random angle
            ))

    # Drawing function for circles
    def draw_circles(self):
        for obj in self.vec_asteroids:
            pygame.draw.circle(self.screen, self.white, (int(obj.x), int(obj.y)), int(obj.n_size / 2))

    # Colilisions
    def check_collisions(self):
        if self.game_over:
            return

        for asteroid in self.vec_asteroids:
            distance = math.sqrt((self.player.x - asteroid.x)**2 + (self.player.y - asteroid.y)**2)
            if distance < (self.player.n_size / 2 + asteroid.n_size / 2):
                print("Game Over")
                self.game_over = True
                self.game_over_time = time.time()

        for asteroid in self.vec_asteroids:
            for bullet in self.vec_bullets:
                distance = math.sqrt((bullet.x - asteroid.x)**2 + (bullet.y - asteroid.y)**2)
                if distance < (asteroid.n_size / 2 + asteroid.n_size / 2):
                    self.vec_asteroids.remove(asteroid)

    # Main setup
    def run_game(self):
        clock = pygame.time.Clock()
        self.create_random_circles(num_circles=5)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.elapsed_time = 0.1
            self.handle_input()
            self.update_objects()
            self.check_collisions()

            self.screen.fill(self.black)
            self.draw_objects()

            if self.game_over:
                if time.time() - self.game_over_time > 3:  # Zakończ grę po 3 sekundach
                    pygame.quit()
                    sys.exit()
                self.screen.fill(self.black)
                font = pygame.font.Font(None, 72)
                game_over_text = font.render("Game Over", True, self.white)
                self.screen.blit(game_over_text, (self.screen_width // 2 - 100, self.screen_height // 2 - 20))
                
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    game = AsteroidsGame(screen_width=1280, screen_height=720)
    game.run_game()