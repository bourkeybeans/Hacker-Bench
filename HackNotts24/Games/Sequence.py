import pygame
import time
from numpy import random
from cs50 import SQL
import sys


if len(sys.argv) < 2:
    print("No session_id provided.")
    sys.exit(1)

session_id = sys.argv[1] 

db = SQL("sqlite:///scores.db")


# Colors
ORANGE = (255, 134, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init()

# Set Window Dimensions
gameWidth = 1000
gameHeight = 800
squareSize = 128
gameDimensions = 5
padding = 10

# Set margins
leftMargin = (gameWidth - (squareSize + padding) * gameDimensions) // 2
topMargin = (gameHeight - (squareSize + padding) * gameDimensions) // 2

screen = pygame.display.set_mode((gameWidth, gameHeight))
pygame.display.set_caption("Sequence Game")

# Draw the grid
def makeGrid(gameDimensions):
    allRect = []
    for x in range(gameDimensions):
        tmp = []
        for y in range(gameDimensions):
            rect = pygame.Rect(
                leftMargin + x * (squareSize + padding),
                topMargin + y * (squareSize + padding),
                squareSize,
                squareSize
            )
            tmp.append(rect)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        allRect.append(tmp)
    pygame.display.flip()
    return allRect

def generateSequence(size):
    seqLen = 8
    coords = []
    selection = list(range(size))
    for _ in range(seqLen):
        xOrd = random.choice(selection)
        yOrd = random.choice(selection)
        coords.append([xOrd, yOrd])
    return coords

# Function to get clicked square coordinates
def getClickedSquare(pos, allRect):
    x, y = pos
    for i in range(len(allRect)):
        for j in range(len(allRect[i])):
            if allRect[i][j].collidepoint(x, y):
                return [i, j]
    return None

def drawText(text, position, size=36):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)
    pygame.display.update(text_rect)

#Initialise the game
screen.fill(ORANGE)
allRect = makeGrid(gameDimensions)
sequence = generateSequence(gameDimensions)
user_sequence = []
game_state = "ready"
current_flash_index = 0
last_flash_time = 0
flash_duration = 500
pause_duration = 500  

# Main game loop
running = True
clock = pygame.time.Clock()
score = 0
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "input":
            clicked_square = getClickedSquare(event.pos, allRect)
            if clicked_square is not None:
                # Visual feedback for click
                i, j = clicked_square
                rect = allRect[i][j]
                pygame.draw.rect(screen, GREEN, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                pygame.display.update(rect)
                pygame.time.delay(200)
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                pygame.display.update(rect)
                
                user_sequence.append(clicked_square)
                
                # Check if the sequence matches so far
                if user_sequence[-1] != sequence[len(user_sequence)-1]:
                    game_state = "lost"
                    screen.fill(ORANGE)
                    makeGrid(gameDimensions)
                    drawText("Wrong sequence! Game Over!", (gameWidth // 2, 50))
                    game_state = "end"
                    #drawText("Press SPACE to play again", (gameWidth // 2, 100))
                elif len(user_sequence) == len(sequence):
                    game_state = "won"
                    screen.fill(ORANGE)
                    makeGrid(gameDimensions)
                    drawText("Congratulations! You won!", (gameWidth // 2, 50))
                    score +=1
                    game_state = "end"
                    #drawText("Press SPACE to play again", (gameWidth // 2, 100))
                else:
                    score +=1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if game_state == "ready":
                # Reset game
                screen.fill(ORANGE)
                allRect = makeGrid(gameDimensions)
                sequence = generateSequence(gameDimensions)
                user_sequence = []
                current_flash_index = 0
                last_flash_time = current_time
                game_state = "showing"
                drawText("Watch the sequence!", (gameWidth // 2, 50))

    # Flashing sequence
    if game_state == "showing":
        time_since_last_flash = current_time - last_flash_time
        
        # If we're showing a square
        if time_since_last_flash < flash_duration:
            i, j = sequence[current_flash_index]
            rect = allRect[i][j]
            pygame.draw.rect(screen, GREEN, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        
        # If we're in the pause between squares
        elif time_since_last_flash < flash_duration + pause_duration:
            i, j = sequence[current_flash_index]
            rect = allRect[i][j]
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        
        # Move to next square or finish sequence
        else:
            if current_flash_index < len(sequence) - 1:
                current_flash_index += 1
                last_flash_time = current_time
            else:
                game_state = "input"
                screen.fill(ORANGE)
                makeGrid(gameDimensions)
                drawText("Your turn! Repeat the sequence", (gameWidth // 2, 50))
    
    # Ready state instructions
    elif game_state == "ready":
        drawText("Press SPACE to start!", (gameWidth // 2, 50))
    elif game_state == "end":
        screen.fill(ORANGE)
        drawText("Your Final Score is: " + str(score), (gameWidth // 2, gameHeight // 2))
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

   

pygame.quit()
print("Your final score is", score)
db.execute("INSERT INTO memory (score, user_id, username) VALUES (?, ?, (SELECT username FROM users WHERE id = ?))",score, session_id, session_id)
        
highestscore = db.execute("SELECT memory FROM highscores WHERE user_id = ?", session_id)
                
highestscore = highestscore[0]
highestscore = highestscore['memory']
if score > highestscore:
    db.execute("UPDATE highscores SET memory = (?) WHERE user_id = ?", score, session_id)
