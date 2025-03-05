"""
  _________  __  __ _____  _____   ______ __  __ _____  ______ __ __ __ __  __ __     ______
  \_  ___  // / / // __  // ____\ \ __  // / / // __  // __  // // // // / / // /    / ____/
   / /__/ // /_/ // / / // /__   / /_/ // /_/ // / / // /_/ // // // // / / // /    / /__
  / _____// __  // / / / \___ \ / ____// __  // / / // _  _// // // // / / // /    / ___/
 / /     / / / // /_/ /_____/ // /    / / / // /_/ // / \ \ \ V  V // /_/ // /___ / /
/_/     /_/ /_//_____//______//_/    /_/ /_//_____//_/  \_\ \__/\_/\_____//_____//_/
"""
import random
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

# Constants
WIDTH, HEIGHT = 600, 600
POP_SIZE = 100
MAX_STEPS = 1000
MUTATION_RATE = 0.001
GENERATIONS = 100

# Goal position
GOAL_X, GOAL_Y = WIDTH - 30, HEIGHT - 30

# Colors
BACKGROUND_COLOR = "light green"
DOT_COLOR = "black"
GOAL_COLOR = "orange"
BEST_DOT_COLOR = "yellow"
OBSTACLE_COLOR = "gray"

class Obstacle:
    """Represents a rectangular obstacle."""
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

    def collides(self, x, y):
        """Check if a point (x, y) is inside the obstacle."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def draw(self, canvas):
        """Draw the obstacle on the Tkinter canvas."""
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=OBSTACLE_COLOR)

# Define obstacles
OBSTACLES = [
    Obstacle(200, 100, 400, 120),
    Obstacle(100, 300, 300, 320),
    Obstacle(350, 450, 550, 470)
]

class Dot:
    def __init__(self):
        self.x, self.y = 30, 30  # Start position
        self.brain = np.random.uniform(-1, 1, (MAX_STEPS, 2))  # Movement directions
        self.step = 0
        self.alive = True
        self.reached_goal = False
        self.fitness = 0

    def move(self):
        if not self.alive or self.step >= MAX_STEPS:
            return

        dx, dy = self.brain[self.step]
        step_size = 10
        new_x = self.x + dx * step_size
        new_y = self.y + dy * step_size

        # Check if the new position is out of bounds
        if new_x < 0 or new_x > WIDTH or new_y < 0 or new_y > HEIGHT:
            self.alive = False  # Stop moving
            return

        # Check for collision with obstacles
        for obstacle in OBSTACLES:
            if obstacle.collides(new_x, new_y):
                self.alive = False  # Stop moving
                return

        # Update position if it's valid
        self.x, self.y = new_x, new_y

        # Check if reached goal
        if abs(self.x - GOAL_X) < 10 and abs(self.y - GOAL_Y) < 10:
            self.reached_goal = True
            self.alive = False  # Stop moving

        self.step += 1
        if self.step >= MAX_STEPS:
            self.alive = False

    def calculate_fitness(self):
        distance_to_goal = np.sqrt((self.x - GOAL_X) ** 2 + (self.y - GOAL_Y) ** 2)
        if self.reached_goal:
            self.fitness = 10_000 + (MAX_STEPS - self.step) * 100  # Huge bonus for fast goal reach
        else:
            self.fitness = 1 / (distance_to_goal + 1)  # Small bonus for getting closer

def reproduce(best_dot):
    new_population = []
    for _ in range(POP_SIZE):
        child = Dot()
        child.brain = np.copy(best_dot.brain)

        # Apply mutations
        for i in range(MAX_STEPS):
            if random.random() < MUTATION_RATE:
                child.brain[i] = np.random.uniform(-1, 1, 2)

        new_population.append(child)
    return new_population

class Pollination:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Genetic Algorithm Maze Solver")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=BACKGROUND_COLOR)
        self.canvas.pack()

        self.generation_label = tk.Label(self.root, text="Generation: 0", font=("Arial", 14))
        self.generation_label.pack()

        self.population = [Dot() for _ in range(POP_SIZE)]
        self.generation = 0
        self.best_brain = None

        self.run_simulation()

    def run_simulation(self):
        if self.generation >= GENERATIONS:
            print("\nBest Dot's Movement Array:\n", self.best_brain)
            self.root.quit()
            return

        for _ in range(MAX_STEPS):
            self.canvas.delete("all")

            # Draw start
            start_image = Image.open("BeeHive.png")
            beehive_png = ImageTk.PhotoImage(start_image)
            self.canvas.create_image(30, 30, image=beehive_png)

            # Draw goal
            goal_image = Image.open("SunFlower.png")
            sunflower_png = ImageTk.PhotoImage(goal_image)
            self.canvas.create_image(GOAL_X+1, GOAL_Y, image=sunflower_png)
            #self.canvas.create_oval(GOAL_X-5, GOAL_Y-5, GOAL_X+5, GOAL_Y+5, fill=GOAL_COLOR)

            # Draw obstacles
            for obstacle in OBSTACLES:
                obstacle.draw(self.canvas)

            # Move and draw dots
            for dot in self.population:
                dot.move()
                self.canvas.create_oval(dot.x-2, dot.y-2, dot.x+2, dot.y+2, fill=DOT_COLOR)

            self.root.update()

        # Evaluate fitness
        for dot in self.population:
            dot.calculate_fitness()

        # Find best dot
        best_dot = max(self.population, key=lambda d: d.fitness)
        self.best_brain = best_dot.brain

        # Display best dot in green
        self.canvas.create_oval(best_dot.x-4, best_dot.y-4, best_dot.x+4, best_dot.y+4, fill=BEST_DOT_COLOR)
        self.generation_label.config(text=f"Generation: {self.generation + 1}")
        self.root.update()

        # Create next generation
        self.population = reproduce(best_dot)
        self.generation += 1
        self.root.after(100, self.run_simulation)

simulator = Pollination()
simulator.root.mainloop()
