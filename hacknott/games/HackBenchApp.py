import pygame

from HackNotts24.hacknott.games.AimTrainer.Assets.config import *
from AimTrainer.AimTrainer import AimTrainer
from OrientationTest.OrientationTest import OrientationTest
from HackNotts24.hacknott.games.OrientationTest.Assets.Model import Model
import sys

if len(sys.argv) < 2:
    print("No session_id provided.")
    sys.exit(1)

session_id = sys.argv[1] 

while __name__ == "__main__":
    pygame.display.set_caption(APP_NAME)
    WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    currentApp = AimTrainer(WIN, 20, session_id ,WIN_WIDTH, WIN_HEIGHT)
    #currentApp = OrientationTest(WIN, FPS, WIN_WIDTH, WIN_HEIGHT)

    while currentApp.running:
        currentApp.app_tick()