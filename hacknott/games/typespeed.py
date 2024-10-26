import random
import time

def get_random_typing_phrase(filename):
    with open(filename, 'r') as file:
        phrases = [line.strip() for line in file if line.strip()]  # Load lines into a list
    return random.choice(phrases)  # Select one line at random


def calculate_penalty(target, user_typed_input):
    penalty = 0
    for i in range(len((target))): 
        if target[i] == user_typed_input[i]:
            penalty += 1
    return penalty

def calculate_wps(characters_typed, time_passed):
    return (characters_typed / 5) / (time_passed / 60)
    

def play():
    filename = 'tests.txt'
    random_phrase = get_random_typing_phrase(filename)
    target = random_phrase
    
    print(random_phrase)
    print("Begin Typing in: ")
    count = 3
    for i in range(3):
        time.sleep(1)
        print(f"{count}")
        count -= 1
    start_time = time.time()
    user_input = input("Type!: ")
    end_time = time.time()
    total_time = end_time - start_time

    wpm = calculate_wps(len(user_input), total_time)
    print(f"Words per Minute = {wpm} ")
    penalty = calculate_penalty(target, user_input)
    print(f"Penalties : {penalty}")
    final_score = max(0, wpm - penalty)  # Ensure the score doesn't go below zero

    print(f"Final Score: {final_score}")
    return final_score



play()