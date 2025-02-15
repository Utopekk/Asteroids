import time
from Utils import Utils
from Settings import *
from CreateManager import CreateManager

N = 4


class HandleManager:
    def __init__(self, player, vec_particles, screen, stage, game_over,
                 vec_huge_asteroids, vec_medium_asteroids, vec_small_asteroids):
        self.game_over = game_over
        self.game_over_time = None
        self.player_respawn_timer = None
        self.vec_huge_asteroids = vec_huge_asteroids
        self.vec_medium_asteroids = vec_medium_asteroids
        self.vec_small_asteroids = vec_small_asteroids
        self.score = 0
        self.score1 = 0
        self.player = player
        self.Utils = Utils()
        self.create_manager = CreateManager(self.player, vec_particles, self.vec_huge_asteroids, self.vec_small_asteroids, screen, stage)

    def handle_game_over(self, reason):
        print(reason)
        self.game_over['status'] = True  # This updates the dictionary reference
        GameOverSound.play()
        self.game_over_time = time.time()

    def handle_player_asteroid_collision(self, asteroid):
        if self.player.destroyed:
            return
        if asteroid in self.vec_huge_asteroids:
            self.vec_huge_asteroids.remove(asteroid)
        elif asteroid in self.vec_medium_asteroids:
            self.Utils.remove_asteroid(asteroid, self.vec_medium_asteroids, self.vec_small_asteroids)
        elif asteroid in self.vec_small_asteroids:
            self.vec_small_asteroids.remove(asteroid)

        self.player.lives -= 1

        if self.player.lives > 0:
            self.create_manager.create_particle_effect(self.player.x, self.player.y, WHITE, 3)
            self.player.destroyed = True
            self.player_respawn_timer = time.time() + 2
            ColisionSound.play()
        else:
            self.handle_game_over("Game Over")

        if not (self.vec_huge_asteroids or self.vec_medium_asteroids or self.vec_small_asteroids):
            self.create_manager.create_random_huge_asteroids(num_asteroids=N)

    def handle_bullet_asteroid_collision(self, asteroid):
        if asteroid in self.vec_huge_asteroids:
            self.score += 20
            self.score1 += 20
            self.vec_huge_asteroids.remove(asteroid)
            medium_asteroid_1 = Utils.med_asteroids(asteroid)
            medium_asteroid_2 = Utils.med_asteroids(asteroid)

            self.vec_medium_asteroids.extend([medium_asteroid_1, medium_asteroid_2])

        elif asteroid in self.vec_medium_asteroids:
            self.score += 50
            self.score1 += 50
            self.Utils.remove_asteroid(asteroid, self.vec_medium_asteroids, self.vec_small_asteroids)

        elif asteroid in self.vec_small_asteroids:
            self.score += 100
            self.score1 += 100
            self.vec_small_asteroids.remove(asteroid)
        self.create_manager.create_particle_effect(asteroid.x, asteroid.y, WHITE, 3)
        return True
