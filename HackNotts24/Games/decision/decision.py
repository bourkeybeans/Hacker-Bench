import pygame
from numpy import random
from cs50 import SQL
import sys


if len(sys.argv) < 2:
    print("No session_id provided.")
    sys.exit(1)

session_id = sys.argv[1] 

db = SQL("sqlite:///scores.db")


dImage = {
    "left": "Games/decision/Decision Game Assets/Left arrow.png",
    "right": "Games/decision/Decision Game Assets/Right arrow.png",
    "X": "Games/decision/Decision Game Assets/X.png"
}

ORANGE = (255, 134, 0)

# Initialize Pygame
pygame.init()

# Set up display dimensions
grid_size = 5
cell_size = 128
padding = 10
screen_width = 1000
screen_height = 800 + 100
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Decision Game")

def getAnswer(display):
    ans = random.choice([0, 1, 2])

    if ans == 1:
        return "left"
    elif ans == 0:
        return "right"
    else:
        display[1][0] = display[1][1] = display[1][3] = display[1][4] = "X"
        return "left" if random.choice([0, 1]) == 1 else "right"

def generatePanel(display):
    for i in range(3):
        tmp = []
        for j in range(5):
            if random.choice([0, 1]) == 1:
                tmp.append("left")
            else:
                tmp.append("right")
        display.append(tmp)
    display[1][2] = getAnswer(display)
    return display

def drawText(text, y_position):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(screen_width // 2, y_position))
    screen.blit(text_surface, text_rect)

# Calculate grid positioning
total_grid_width = grid_size * cell_size + (grid_size - 1) * padding
total_grid_height = grid_size * cell_size + (grid_size - 1) * padding
start_x = (screen_width - total_grid_width) // 2
start_y = (screen_height - total_grid_height) // 2

# Add margin for text
text_margin = 200  # Space for text above grid
start_y += text_margin  # Move grid down to make room for text at top

# Load and scale images
images = []
display = generatePanel([])
for row in display:
    for el in row:
        img = pygame.image.load(dImage[el])
        img = pygame.transform.scale(img, (cell_size, cell_size))
        images.append(img)

score = 0
count = 0
gameState = "begin"

clock = pygame.time.Clock()

# Main event loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or count == 20:
            running = False
            endTime = pygame.time.get_ticks()
        elif gameState == "userTurn":
            # Fill background color
            screen.fill(ORANGE)
            
            # Draw instructions with proper spacing
            drawText("Press Q if the middle element is left", 50)
            drawText("Press P if the middle element is right", 90)
            drawText("Press BackSpace if any element has a 'X'", 130)

            # Draw images in a 5x5 grid
            for row in range(grid_size):
                for col in range(grid_size):
                    index = row * grid_size + col
                    if index < len(images):  # Ensure index is valid
                        x = start_x + col * (cell_size + padding)
                        y = start_y + row * (cell_size + padding)
                        screen.blit(images[index], (x, y))

            # Check key press events for user input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and display[1][2] == "left" and display[1][0] != "X":
                    score += 1
                elif event.key == pygame.K_p and display[1][2] == "right" and display[1][0] != "X":
                    score += 1
                elif event.key == pygame.K_BACKSPACE and display[1][0] == "X":
                    score += 1
                gameState = "refresh"
                count += 1

        elif gameState == "refresh":

            drawText("Press Q if the middle element is left", 50)
            drawText("Press P if the middle element is right", 90)
            drawText("Press BackSpace if any element has a 'X'", 130)
            # Get new values for image display
            images = []
            display = generatePanel([])
            screen.fill(ORANGE)
            for row in display:
                for el in row:
                    img = pygame.image.load(dImage[el])
                    img = pygame.transform.scale(img, (cell_size, cell_size))
                    images.append(img)

            # Draw images in a 5x5 grid
            for row in range(grid_size):
                for col in range(grid_size):
                    index = row * grid_size + col
                    if index < len(images):  # Ensure index is valid
                        x = start_x + col * (cell_size + padding)
                        y = start_y + row * (cell_size + padding)
                        screen.blit(images[index], (x, y))

            gameState = "userTurn"

        elif gameState == "begin":
            if(event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                gameState = "userTurn"

            screen.fill(ORANGE)

            # Draw images in a 5x5 grid
            for row in range(grid_size):
                for col in range(grid_size):
                    index = row * grid_size + col
                    if index < len(images): 
                        x = start_x + col * (cell_size + padding)
                        y = start_y + row * (cell_size + padding)
                        screen.blit(images[index], (x, y))

            drawText("Press Q if the middle element is left", 50)
            drawText("Press P if the middle element is right", 90)
            drawText("Press BackSpace if any element has a 'X'", 130)
            drawText("Press Spacebar to begin", 170)
            startTime = pygame.time.get_ticks()

        elif count == 10:
            screen.fill(ORANGE)
            time = endTime - startTime
            drawText("Your final Score is " + str(score - (time // 1990) ), screen_width // 2,  screen_height // 2)


    pygame.display.flip()

time = endTime - startTime
print("Correct answers:",score)
#Take the value below to store in the database
print("Final Score:", 1000 - ((count - score) + (time/100)))
score = 1000 - ((count - score) + (time/100))

db.execute("INSERT INTO decision (score, user_id, username) VALUES (?, ?, (SELECT username FROM users WHERE id = ?))",score, session_id, session_id)
        
highestscore = db.execute("SELECT decision FROM highscores WHERE user_id = ?", session_id)
                
highestscore = highestscore[0]
highestscore = highestscore['decision']
if score > highestscore:
    db.execute("UPDATE highscores SET decision = (?) WHERE user_id = ?", score, session_id)


# Quit Pygame
pygame.quit()
