# Code based off Tech With Tim's Python Aim Trainer Youtube video
# Added some additional code/features -> play again feature and best stats feature

import math
import random
import time
import pygame
pygame.init()

# pixels for the pygame window
WIDTH, HEIGHT = 800, 600

# initializes the pygame window and imports the height and width
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 400 #400 milliseconds
TARGET_EVENT = pygame.USEREVENT 
TARGET_PADDING = 30 # How many pixels off the screen
LIVES = 5 # How many lives you get
RIBBON_HEIGHT = 50

LABEL_FONT = pygame.font.SysFont("comicsans", 24)

best_time = 0
highest_speed = 0
most_hits = 0
highest_accuracy = 0

class Target:
    MAX_SIZE = 20 # Max size of target
    GROWTH_RATE = 0.3 # Growth rate in pixels per frame
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
    
    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        # Moniters if target is growing or shrinking
        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE
    
    def draw(self, win): # Draws the target
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y): # Calculates if the mouse is within the radius of the circle to track a click
        distance = math.sqrt((self.x - x)**2 + (self.y - y)**2)
        return distance <= self.size

def draw(win, targets):
    # Background color
    win.fill("black")

    for target in targets:
        target.draw(win)

def format_time(sec): # Creates the time label
    milliseconds = math.floor(int(sec * 1000 % 1000 / 100)) # Calculates milliseconds
    seconds = int(round(sec % 60, 1))
    minutes = int(sec // 60)

    return f"{minutes:1d}:{seconds:02d}.{milliseconds}"

def ribbon(win, elapsed_time, targets_pressed, misses): # Creates the ribbon
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, RIBBON_HEIGHT))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")

    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} targets/sec", 1, "black")

    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")

    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")
    
    # Creates the label
    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (500, 5))
    win.blit(lives_label, (650, 5))

def end_screen(win, elapsed_time, targets_pressed, clicks):
    win.fill("black")
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} targets/sec", 1, "white")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")
    try: 
        accuracy = round(targets_pressed / clicks * 100, 2)
    except ZeroDivisionError as e: 
        accuracy = 0.0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")

    # New Code ->
    show_restart = LABEL_FONT.render("Press Space to Restart", True, "white")

    previous_time = elapsed_time
    previous_speed = speed
    previous_hits = targets_pressed
    previous_accuracy = accuracy

    global best_time
    global highest_speed
    global most_hits
    global highest_accuracy

    if previous_time > best_time:
        best_time = previous_time
    if previous_speed > highest_speed:
        highest_speed = previous_speed                    
    if previous_hits > most_hits:
        most_hits = previous_hits
    if previous_accuracy > highest_accuracy:
        highest_accuracy = previous_accuracy
    
    best1 = LABEL_FONT.render(f"BEST TIME: {format_time(best_time)}", 1, "white")
    best2 = LABEL_FONT.render(f"HIGHEST SPEED: {highest_speed} targets/sec", 1, "white")
    best3 = LABEL_FONT.render(f"MOST HITS: {most_hits}", 1, "white")
    best4 = LABEL_FONT.render(f"HIGHEST ACCURACY: {highest_accuracy}%", 1, "white")

    # Most recent data
    win.blit(time_label, (get_middle(time_label), 30))
    win.blit(speed_label, (get_middle(speed_label), 70))
    win.blit(hits_label, (get_middle(hits_label), 120))
    win.blit(accuracy_label, (get_middle(accuracy_label), 170))
    win.blit(show_restart, (get_middle(show_restart), 290))
    
    # Best data
    win.blit(best1, (get_middle(best1), 400))
    win.blit(best2, (get_middle(best2), 450))
    win.blit(best3, (get_middle(best3), 500))
    win.blit(best4, (get_middle(best4), 550))

    pygame.display.update()

    run = True
    # This loop will moniter the end screen and will quit the program if action is taken
    while run: 
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # If you press space the game will restart
                    pygame.display.update()
                    run = False
                    main()
                    break
            elif event.type == pygame.QUIT:
                quit()

def get_middle(surface): # Will draw an end screen in the middle of the tab
    return WIDTH / 2 - surface.get_width() / 2

def main():
    run = True
    targets = []
    clock = pygame.time.Clock()

    target_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()

    # Triggers the target event with an interval of the target increment
    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    # Checks if the tab closes and will shut down the game
    while run:
        clock.tick(60) # Will run at 60 fps
        click = False
        mouse_pos = pygame.mouse.get_pos() # Gives the x and y coordinate of the mouse
        elapsed_time = time.time() - start_time # Shows us elapsed time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            # Creates a random position of target 
            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + RIBBON_HEIGHT, HEIGHT - TARGET_PADDING)
                target = Target(x, y)
                targets.append(target)

            # Counts how many clicks on the target
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        for target in targets:
            target.update()

            # Will remove the target if the size is 0 and will track how many misses on target
            if target.size <= 0:
                targets.remove(target)
                misses += 1

            # Will break down the x and y coordinates of mouse
            if click and target.collide(*mouse_pos):
                targets.remove(target)
                target_pressed += 1

        # Will end the game if you run out of lives (misses)
        if misses >= LIVES:
            end_screen(WIN, elapsed_time, target_pressed, clicks)
            
        draw(WIN, targets)
        ribbon(WIN, elapsed_time, target_pressed, misses)
        pygame.display.update()

# Only runs the main function if the file is executed directly
if __name__ == "__main__":
    main()



