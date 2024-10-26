import pygame
import random

from Target import Target

# Colours
ORANGE = (255, 134, 0)

pygame.init()


class AimTrainer():
    def __init__(self, surface, WIDTH=1000, HEIGHT=800):
        # Initialise Default Perimeters for the PyGame Window
        self.WIN = surface
        self.running = True
        self.__WIDTH = WIDTH
        self.__HEIGHT = HEIGHT

        self.currentTarget = Target((100, 100))


    def draw_window(self):
        'Draws the UI to the screen'
        
        self.WIN.fill(ORANGE)

        self.currentTarget.draw(self.WIN)
        
        pygame.display.update()


    def generate_target(self):
        'Generates a new target'

        x = random.randint(self.currentTarget.image.get_width()//2, self.__WIDTH - self.currentTarget.image.get_width())
        y = random.randint(0, self.__HEIGHT - self.currentTarget.image.get_height())

        self.currentTarget = Target((x, y))


    def app_tick(self):
        'Handles all of the app logic on each tick'

        for event in pygame.event.get():
            # Quits application if 'X' button on the window is pressed
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                # Quits application if escape key is pressed
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    exit()

        if self.currentTarget.is_clicked():
            self.generate_target()

        self.draw_window()


while __name__ == "__main__":
    # Initialises the constants and creates pygame window
    FPS = 120
    WIDTH, HEIGHT = 1000, 800
    pygame.display.set_caption("AimTrainer")
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    currentApp = AimTrainer(WIN, WIDTH, HEIGHT)

    while currentApp.running:
        currentApp.app_tick()