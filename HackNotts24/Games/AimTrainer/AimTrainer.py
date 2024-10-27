import pygame
import random

from Assets.config import *
from Assets.Target import Target
from cs50 import SQL
import sys

db = SQL("sqlite:///scores.db")


if len(sys.argv) < 2:
    print("No session_id provided.")
    sys.exit(1)

session_id = sys.argv[1] 

class AimTrainer():
    def __init__(self, surface:pygame.surface, sessionID:str, startTargets:int=20, WIDTH:int=1000, HEIGHT:int=800):
        # Initialise Default Perimeters for the PyGame Window
        self.WIN = surface
        self.running = True
        self.__WIDTH = WIDTH
        self.__HEIGHT = HEIGHT
        self.sessionID = sessionID

        # Initialise Starting Text
        self.__startingTitle = TITLE_FONT.render('Aim Trainer', True, PURPLE)
        self.__startingSubTitle = SUBTITLE_FONT.render(f'Click {startTargets} Targets as fast as you can', True, PURPLE)

        # Initialise Targets
        self.currentTarget = Target((self.__WIDTH/2, self.__HEIGHT/2))

        self.__startingTargets = startTargets
        self.__targetsRemaining = startTargets
        self.__times = []


    def draw_window(self) -> None:
        'Draws the UI to the screen'
        
        self.WIN.fill(ORANGE)

        # Drawing the target
        self.currentTarget.draw(self.WIN)

        # Drawing the remaining text
        if self.__targetsRemaining > 0:
            remainingText = SUBTITLE_FONT.render(f'Remaining: {self.__targetsRemaining}', True, PURPLE)
            remainingTextRect = remainingText.get_rect(midtop = (self.__WIDTH/2, 10))
            self.WIN.blit(remainingText, remainingTextRect)

        # Drawing the start of game text
        if self.__targetsRemaining == self.__startingTargets:
            titleTextRect = self.__startingTitle.get_rect(center = (self.__WIDTH/2, (self.__HEIGHT/2)-60))
            subtitleTextRect = self.__startingSubTitle.get_rect(center = (self.__WIDTH/2, (self.__HEIGHT/2)+60))
            self.WIN.blit(self.__startingTitle, titleTextRect)
            self.WIN.blit(self.__startingSubTitle, subtitleTextRect)

        # Drawing the end of game information
        if self.__targetsRemaining == 0:
            endText = SUBTITLE_FONT.render('Average time per target:', True, PURPLE)
            endTextRect = endText.get_rect(center = (self.__WIDTH/2, self.__HEIGHT/2-60))
            endTime = TITLE_FONT.render(f'{self.get_average_time()*1000:.1f}ms', True, DARK_PURPLE)
            endTimeRect = endTime.get_rect(center = (self.__WIDTH/2, self.__HEIGHT/2))

            self.WIN.blit(endText, endTextRect)
            self.WIN.blit(endTime, endTimeRect)
        
        pygame.display.update()
    

    def get_average_time(self) -> float:
        'Returns the average time to click each target'

        return sum(self.__times[1:]) / len(self.__times)


    def generate_target(self) -> None:
        'Generates a new target'

        if self.__targetsRemaining > 0:
            self.__times.append(self.currentTarget.get_end_time())
            x = random.randint(self.currentTarget.image.get_width()//2, self.__WIDTH - self.currentTarget.image.get_width()//2)
            y = random.randint(self.currentTarget.image.get_height()//2, self.__HEIGHT - self.currentTarget.image.get_height()//2)

            self.currentTarget = Target((x, y))

        else:
            self.currentTarget = Target((self.__WIDTH/2, self.__HEIGHT/2+150), True)


    def app_tick(self) -> None:
        'Handles all of the app logic on each tick'

        for event in pygame.event.get():
            # Quits application if 'X' button on the window is pressed
            if event.type == pygame.QUIT:
                db.execute("INSERT INTO aim (score, user_id, username) VALUES (?, ?, (SELECT username FROM users WHERE id = ?))",self.get_average_time()*1000, session_id, session_id)
        
                highestscore = db.execute("SELECT aim FROM highscores WHERE user_id = ?", session_id)
                
                highestscore = highestscore[0]
                highestscore = highestscore['aim']
                if self.get_average_time()*1000 < highestscore or highestscore == 0:
                    db.execute("UPDATE highscores SET aim = (?) WHERE user_id = ?", self.get_average_time()*1000, session_id)
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                # Quits application if escape key is pressed
                if event.key == pygame.K_ESCAPE:
                    db.execute("INSERT INTO aim (score, user_id, username) VALUES (?, ?, (SELECT username FROM users WHERE id = ?))",self.get_average_time()*1000, session_id, session_id)
        
                    highestscore = db.execute("SELECT aim FROM highscores WHERE user_id = ?", session_id)
                
                    highestscore = highestscore[0]
                    highestscore = highestscore['aim']
                    if self.get_average_time()*1000 < highestscore or highestscore == 0:
                        db.execute("UPDATE highscores SET aim = (?) WHERE user_id = ?", self.get_average_time()*1000, session_id)
                    self.running = False
                    pygame.quit()
                    exit()

        if self.currentTarget.is_clicked() and self.__targetsRemaining > 0:
            self.__targetsRemaining -= 1
            self.generate_target()

        self.draw_window()


while __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No session_id provided.")
        sys.exit(1)

    sessionID = sys.argv[1] 

    pygame.display.set_caption(APP_NAME)
    WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    currentApp = AimTrainer(WIN, sessionID, 20,  WIN_WIDTH, WIN_HEIGHT)

    while currentApp.running:
        currentApp.app_tick()