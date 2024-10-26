import pygame

class Target:
    def __init__(self, coordinates: tuple):
        'Initialises the textures as coordinates for the button'
        
        self.image = pygame.image.load('Assets/target.png')

        self.coordinates = coordinates
        self.target_rect = self.image.get_rect(topleft=self.coordinates)
        self.clicked = False


    def is_clicked(self):
        'Returns True if the button is clicked, and False if button is not clicked'

        mouse_pos = pygame.mouse.get_pos()
        
        if pygame.mouse.get_pressed()[0] and self.target_rect.collidepoint(mouse_pos):
            self.clicked = True

        elif self.clicked:
            return True

        else:
            self.clicked = False


    def draw(self, surface:pygame.surface):
        'Draws the target to the provided surface'
        
        surface.blit(self.image, self.coordinates)
        