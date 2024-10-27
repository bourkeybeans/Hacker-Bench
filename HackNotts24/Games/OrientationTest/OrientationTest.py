import numpy as np
import pygame
import random
import time
from math import *
from cs50 import SQL

from Assets.config import *
from Model import Model
import sys

if len(sys.argv) < 2:
    print("No session_id provided.")
    sys.exit(1)

session_id = sys.argv[1] 

db = SQL("sqlite:///scores.db")


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
        self.__SENSITIVITY = 57.35

        # Initialises the default parameters for cube angle
        self.scale = 5
        self.xAngle = random.randint(0, 6300) / 1000
        self.yAngle = random.randint(0, 6300) / 1000
        self.__startXAngle = (self.xAngle*self.__SENSITIVITY)%360
        self.__startYAngle = (self.xAngle*self.__SENSITIVITY)%360
        if self.__startYAngle >= 90 and self.__startYAngle <= 270:
            self.__startXAngle = (180+self.__startXAngle)%360
        self.previousX = None
        self.previousY = None

        self.currentModel = Model('shark.obj')
        self.__stage = 'Memorise'

        self.__timerStart = time.perf_counter()
        self.__testCountdownStart = None
        
        # Creates placeholder values for the projected points array
        self.projected_points = [[n, n] for n in range(len(self.currentModel.vertices))]


    def project_points(self) -> None:
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

        # Determines how much the mouse has moved in the x direction
        if self.previousX == None: self.previousX = pygame.mouse.get_pos()[0]
        currentX = pygame.mouse.get_pos()[0]
        xChange, self.previousX = currentX - self.previousX, currentX

        # Determines how much the mouse has moved in the y direction
        if self.previousY == None: self.previousY = pygame.mouse.get_pos()[1]
        currentY = pygame.mouse.get_pos()[1]
        yChange, self.previousY = currentY - self.previousY, currentY

        # Updates the x and y angles based on the determined movement
        self.xAngle += xChange/100
        self.yAngle -= yChange/100

        # Calculates the circular angle between 0 and 360
        self.circleXAngle = (self.xAngle*self.__SENSITIVITY)%360
        self.circleYAngle = (self.yAngle*self.__SENSITIVITY)%360

        # If cube is upside down, adds 180˚ to x circular angle
        if self.circleYAngle >= 90 and self.circleYAngle <= 270:
            self.circleXAngle = (180+self.circleXAngle)%360
            
            # Inverses mvement in the x direction
            self.xAngle += 2*(-xChange/100)
    

    def calc_final_score(self) -> None:
        def angular_difference(angle1:float, angle2:float) -> float:
            diff = abs(angle1 - angle2) % 360
            return min(diff, 360 - diff)

        tolerance = 12

        diffX = angular_difference(self.__startXAngle, self.circleXAngle)
        diffY = angular_difference(self.__startYAngle, self.circleYAngle)

        maxDifference = 180

        def calculate_score(diff):
            if diff <= tolerance:
                return 100
            else:
                adjustedDiff = diff - tolerance
                return (1 - (adjustedDiff / (maxDifference - tolerance))) * 100

        scoreX = calculate_score(diffX)
        scoreY = calculate_score(diffY)


        self.finalScore = int((scoreX + scoreY) / 2)


    def draw_wireframe(self) -> None:
        for (e1, e2) in self.currentModel.edges:
            pygame.draw.line(self.WIN, ORANGE, self.projected_points[e1], self.projected_points[e2], 2)


    def draw_window(self) -> None:
        'Draws the UI to the screen'
        
        self.WIN.fill(DARK_PURPLE)

        if self.__stage == 'Memorise':
            memoryText = SUBTITLE_FONT.render('Memorise the current position of the model!', True, ORANGE)
            memoryTextRect = memoryText.get_rect(midtop = (self.__WIDTH/2, 10))
            timerText = TITLE_FONT.render(f'{5 - (time.perf_counter() - self.__timerStart):1.1f}', True, ORANGE)
            timerTextRect = timerText.get_rect(midbottom = (self.__WIDTH/2, self.__HEIGHT - 10))
            
            self.WIN.blit(memoryText, memoryTextRect)
            self.WIN.blit(timerText, timerTextRect)

        elif self.__stage == 'Test' and self.__testCountdownStart:
            returnText = SUBTITLE_FONT.render('Return the model to it\'s previous state!', True, ORANGE)
            returnTextRect = returnText.get_rect(midtop = (self.__WIDTH/2, 10))
            timerText = TITLE_FONT.render(f'{10 - (time.perf_counter() - self.__testCountdownStart):1.1f}', True, ORANGE)
            timerTextRect = timerText.get_rect(midbottom = (self.__WIDTH/2, self.__HEIGHT - 10))
            
            self.WIN.blit(returnText, returnTextRect)
            self.WIN.blit(timerText, timerTextRect)

        elif self.__stage == 'End':
            scoreText = TITLE_FONT.render(f'You scored {self.finalScore}%', True, ORANGE)
            scoreTextRect = scoreText.get_rect(midtop = (self.__WIDTH/2, 50))

            self.WIN.blit(scoreText, scoreTextRect)

        self.project_points()

        self.draw_wireframe()

        pygame.display.update()


    def app_tick(self) -> None:
        'Handles all of the app logic on each tick'

        if 5 - (time.perf_counter() - self.__timerStart) < 0 and not self.__testCountdownStart:
            self.__stage = 'Test'
            self.__testCountdownStart = time.perf_counter()
            self.xAngle = random.randint(-10000, 10000) / 1000  # Randomise angle of model for solving
            self.yAngle = random.randint(-10000, 10000) / 1000  # Randomise angle of model for solving

        if self.__testCountdownStart and 10 - (time.perf_counter() - self.__testCountdownStart) < 0:
            self.__stage = 'End'
            self.calc_final_score()

        # Handles the logic when left click is pressed on the mouse
        if self.__stage == 'Test' and pygame.mouse.get_pressed()[0]:
            self.handle_mouse_movement()

        for event in pygame.event.get():
            # Quits application if 'X' button on the window is pressed
            if event.type == pygame.QUIT:
                score = self.finalScore
                db.execute("INSERT INTO threedee (score, user_id, username) VALUES (?, ?, (SELECT username FROM users WHERE id = ?))",score, session_id, session_id)
        
                highestscore = db.execute("SELECT threedee FROM highscores WHERE user_id = ?", session_id)
                
                highestscore = highestscore[0]
                highestscore = highestscore['threedee']
                if score > highestscore:
                    db.execute("UPDATE highscores SET threedee = (?) WHERE user_id = ?", score, session_id)
                self.running = False
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                score = self.finalScore
                db.execute("INSERT INTO threedee (score, user_id, username) VALUES (?, ?, (SELECT username FROM users WHERE id = ?))",score, session_id, session_id)
        
                highestscore = db.execute("SELECT threedee FROM highscores WHERE user_id = ?", session_id)
                
                highestscore = highestscore[0]
                highestscore = highestscore['threedee']
                if score > highestscore:
                    db.execute("UPDATE highscores SET threedee = (?) WHERE user_id = ?", score, session_id)
                # Quits application if escape key is pressed
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    exit()

            # Resets mouse movement when left click isn't pressed
            if event.type == pygame.MOUSEBUTTONUP:
                self.previousY = None
                self.previousX = None

        # Updates rotation matrices with the current perspective angles
        self.rotation_x = np.matrix([[1, 0, 0],
                                     [0, cos(self.yAngle), -sin(self.yAngle)],
                                     [0, sin(self.yAngle), cos(self.yAngle)]])

        self.rotation_y = np.matrix([[cos(self.xAngle), 0, sin(self.xAngle)],
                                     [0, 1, 0],
                                     [-sin(self.xAngle), 0, cos(self.xAngle)]])

        # After all logic for tick has been handled, window is drawn
        self.draw_window()


if __name__ == "__main__":
    loadedModel = Model('shark.obj')

    pygame.display.set_caption(APP_NAME)
    WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    app = OrientationTest(WIN, FPS, WIN_WIDTH, WIN_HEIGHT)

    clock = pygame.time.Clock()
    
    while app.running:
        clock.tick(FPS)
        app.app_tick()