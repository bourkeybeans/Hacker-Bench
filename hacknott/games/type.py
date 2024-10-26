import pygame
import time
import random
import difflib
from cs50 import SQL
import sys

if len(sys.argv) < 2:
    print("No session_id provided.")
    sys.exit(1)

session_id = sys.argv[1] 

# Database connection
db = SQL("sqlite:///scores.db")

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 1500
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Typing Game")

# Font settings
font = pygame.font.Font(None, 48)

def get_random_typing_phrase(filename):
    with open(filename, 'r') as file:
        phrases = [line.strip() for line in file if line.strip()]
    return random.choice(phrases)

def calculate_wpm(typed_text, elapsed_time):
    total_characters = len(typed_text)
    total_words = total_characters / 5
    total_time_minutes = elapsed_time / 60
    return total_words / total_time_minutes

def calculate_penalty(target, user_input):
    diff = difflib.ndiff(target, user_input)
    mistakes = sum(1 for d in diff if d[0] != ' ')
    return mistakes

def calculate_score(wpm, penalty):
    return max(0, wpm - penalty)

def wrap_text(text, font, max_width):
    """Breaks text into multiple lines based on max_width."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    
    lines.append(current_line)  # Add the last line
    return lines

def display_text(text, y_offset, line_height=50, max_width=1400):
    """Displays wrapped text on the screen with multiple lines."""
    lines = wrap_text(text, font, max_width)
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (50, y_offset))
        y_offset += line_height  # Move down for the next line

def main():
    # Load the target phrase
    filename = 'tests.txt'
    target_phrase = get_random_typing_phrase(filename)
    user_input = ""
    game_started = False

    # Main loop
    running = True
    while running:
        screen.fill((255, 255, 255))  # Clear screen with white background

        # Display the target phrase at the top
        display_text("Type the following phrase:", 50)
        display_text(target_phrase, 100)

        # Draw a box for the user input area
        pygame.draw.rect(screen, (230, 230, 250), (50, 400, 1400, 100))  # Light blue box for user input
        display_text("Your input:", 350)  # Label above input box

        # Display user input inside the box
        user_input_lines = wrap_text(user_input, font, 1400)
        y_offset = 420  # Start y position inside the input box
        for line in user_input_lines:
            text_surface = font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (60, y_offset))
            y_offset += 50  # Line height

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Start the game on first key press
                if not game_started:
                    start_time = time.time()
                    game_started = True
                
                # Capture user input
                if event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]  # Remove last character
                elif event.key == pygame.K_RETURN:
                    # Game over, calculate score
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    
                    # Calculate WPM and penalties
                    wpm = calculate_wpm(user_input, elapsed_time)
                    penalty = calculate_penalty(target_phrase, user_input)
                    score = calculate_score(wpm, penalty)

                    # Display results
                    screen.fill((255, 255, 255))  # Clear screen
                    display_text(f"Time taken: {elapsed_time:.2f} seconds", 50)
                    display_text(f"Your WPM: {wpm:.2f}", 100)
                    display_text(f"Penalties: {penalty}", 150)
                    display_text(f"Your final score: {score:.2f}", 200)
                    pygame.display.flip()

                

                    # Pause to show the final score, then exit the game
                    pygame.time.wait(5000)  # Wait 5 seconds to show results
                    db.execute("INSERT INTO type (wpm, penalties, score, user_id, username) VALUES (?, ?, ?, ?, (SELECT username FROM users WHERE id = ?))",wpm, penalty, score, session_id, session_id)
        
                    highestscore = db.execute("SELECT typing FROM highscores WHERE user_id = ?", session_id)
                
                    highestscore = highestscore[0]
                    highestscore = highestscore['typing']
                    if score > highestscore:
                        db.execute("UPDATE highscores SET typing = (?) WHERE user_id = ?", score, session_id)
                    running = False  # End the main loop to exit the game
                else:
                    # Add character to user input if it's a valid key
                    if event.unicode:
                        user_input += event.unicode

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
