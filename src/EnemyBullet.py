from SpaceObject import SpaceObject
import time

class EnemyBullet(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, acceleration):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = acceleration
        self.can_damage_enemy = False
        self.damage_activation_time = time.time() + 0.5