import math


class Stage:
    def __init__(self, stage):
        self.stage = stage
        self.intervalSpawning = 0.15 * stage 
        if self.intervalSpawning > 1.25:
            self.intervalSpawning = 1.25
        self.newAsteroids = math.floor(4 + 1/2 * stage)
        self.asteroidDifficultySize = math.floor(4 * 1/2 * stage)
        if self.asteroidDifficultySize > 35:
            self.asteroidDifficultySize = 35