import pygame

from config import *
from AimTrainer.AimTrainer import AimTrainer
from OrientationTest.OrientationTest import OrientationTest
from OrientationTest.Model import Model

while __name__ == "__main__":
    pygame.display.set_caption(APP_NAME)
    WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    #currentApp = AimTrainer(WIN, 20, WIN_WIDTH, WIN_HEIGHT)
    currentApp = OrientationTest(WIN, FPS, WIN_WIDTH, WIN_HEIGHT)

    while currentApp.running:
        currentApp.app_tick()