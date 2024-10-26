import numpy as np
import pygame
import random
from math import *

from HackNotts24.hacknott.games.AimTrainer.Assets.config import *
from HackNotts24.hacknott.games.OrientationTest.Assets.Model import Model


# Initialises the projection matrix
PROJECTION_MATRIX = np.matrix([[1, 0, 0],
                               [0, 1, 0]])


class OrientationTest():
    def __init__(self, surface:pygame.surface, FPS:int, WIDTH=1000, HEIGHT=800) -> None:
        # Sets the app perameters based on the passed arguments
        self.WIN = surface
        self.FPS = FPS
        self.running = True
        
        # Initialses constant values for the UI
        self.__HEIGHT = HEIGHT
        self.__WIDTH = WIDTH
        self.__CENTRE_OFFSET = [WIDTH/2, HEIGHT/2]

        # Initialises the default parameters for cube angle
        self.scale = 1280
        self.x_angle = random.randint(-10000, 10000) / 1000
        self.y_angle = random.randint(-10000, 10000) / 1000
        self.previous_x = None
        self.previous_y = None

        self.currentModel = Model('trophy.obj')
        
        # Creates placeholder values for the projected points array
        self.projected_points = [[n, n] for n in range(len(self.currentModel.vertices))]


    def project_points(self):
        'Projects self.points from [x, y, z] coordinates to [x, y] coordinates in self.projected_points'
        
        i = 0
        for point in self.currentModel.vertices:
            # Multiplies point by rotation matrices
            rotated2d = np.dot(self.rotation_y, point.reshape(3, 1))
            rotated2d = np.dot(self.rotation_x, rotated2d)

            # Multiplies point by projectoin matrix to convert to 3D points
            projected2d = np.dot(PROJECTION_MATRIX, rotated2d)

            x = int((projected2d[0][0]) * self.scale) + self.__CENTRE_OFFSET[0] 
            y = int((projected2d[1][0]) * self.scale) + self.__CENTRE_OFFSET[1]
            
            # Assigns points to their corresponding location in projected points
            self.projected_points[i] = [x, y]
            i += 1


    def handle_mouse_movement(self) -> None:
        'Handles mouse movement at app runtime'
        
        SENSITIVITY = 57.35

        # Determines how much the mouse has moved in the x direction
        if self.previous_x == None: self.previous_x = pygame.mouse.get_pos()[0]
        current_x = pygame.mouse.get_pos()[0]
        x_change, self.previous_x = current_x - self.previous_x, current_x

        # Determines how much the mouse has moved in the y direction
        if self.previous_y == None: self.previous_y = pygame.mouse.get_pos()[1]
        current_y = pygame.mouse.get_pos()[1]
        y_change, self.previous_y = current_y - self.previous_y, current_y

        # Updates the x and y angles based on the determined movement
        self.x_angle += x_change/100
        self.y_angle -= y_change/100

        # Calculates the circular angle between 0 and 360
        self.circle_x_angle = (self.x_angle*SENSITIVITY)%360
        self.circle_y_angle = (self.y_angle*SENSITIVITY)%360

        # If cube is upside down, adds 180˚ to x circular angle
        if self.circle_y_angle >= 90 and self.circle_y_angle <= 270:
            self.circle_x_angle = (180+self.circle_x_angle)%360
            
            # Inverses mvement in the x direction
            self.x_angle += 2*(-x_change/100)


    def draw_wireframe(self) -> None:
        for (e1, e2) in self.currentModel.edges:
            pygame.draw.line(self.WIN, ORANGE, self.projected_points[e1], self.projected_points[e2], 2)


    def draw_window(self) -> None:
        'Draws the UI to the screen'
        
        self.WIN.fill(DARK_PURPLE)

        self.project_points()

        self.draw_wireframe()

        pygame.display.update()


    def app_tick(self) -> None:
        'Handles all of the app logic on each tick'

        # Handles the logic when left click is pressed on the mouse
        if pygame.mouse.get_pressed()[0]:
            self.handle_mouse_movement()

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

            # Resets mouse movement when left click isn't pressed
            if event.type == pygame.MOUSEBUTTONUP:
                self.previous_y = None
                self.previous_x = None

            '''if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.scale -= 20
                elif event.y < 0:
                    self.scale += 20
                print(f'Scale: {self.scale}')'''

        # Updates rotation matrices with the current perspective angles
        self.rotation_x = np.matrix([[1, 0, 0],
                                     [0, cos(self.y_angle), -sin(self.y_angle)],
                                     [0, sin(self.y_angle), cos(self.y_angle)]])

        self.rotation_y = np.matrix([[cos(self.x_angle), 0, sin(self.x_angle)],
                                     [0, 1, 0],
                                     [-sin(self.x_angle), 0, cos(self.x_angle)]])

        # After all logic for tick has been handled, window is drawn
        self.draw_window()


if __name__ == "__main__":
    loadedModel = Model('trophy.obj')

    pygame.display.set_caption(APP_NAME)
    WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    app = OrientationTest(WIN, FPS, loadedModel, WIN_WIDTH, WIN_HEIGHT)

    clock = pygame.time.Clock()
    
    while app.running:
        clock.tick(FPS)
        app.app_tick()