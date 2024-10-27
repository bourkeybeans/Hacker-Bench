import pygame
import time


class Target:
    def __init__(self, coordinates: tuple, scale:bool=False) -> None:
        'Initialises the textures as coordinates for the button'
        
        # Initialises image and location
        self.coordinates = coordinates
        if scale:
            self.image = pygame.transform.scale2x(pygame.image.load('Games/AimTrainer/Assets/target.png'))
        else:
            self.image = pygame.image.load('Games/AimTrainer/Assets/target.png')
        self.targetRect = self.image.get_rect(center=self.coordinates)
        
        # Initialises local variables
        self.__clicked = False
        self.__startTime = time.perf_counter()


    def get_end_time(self) -> float:
        return time.perf_counter() - self.__startTime


    def is_clicked(self) -> bool:
        'Returns True if the target is clicked, and False if button is not clicked'

        mousePos = pygame.mouse.get_pos()
        
        if pygame.mouse.get_pressed()[0] and self.targetRect.collidepoint(mousePos):
            self.__clicked = True

        elif self.__clicked:
            return True

        else:
            self.__clicked = False


    def draw(self, surface:pygame.surface) -> None:
        'Draws the target to the provided surface'
        
        surface.blit(self.image, self.targetRect)
        