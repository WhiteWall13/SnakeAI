# This is the corrected code for the snake game.
# It should be run in a local Python environment, not in this notebook.

import pygame
import random
import matplotlib.pyplot as plt

# Define the colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game dimensions
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480
GRIDSIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRIDSIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRIDSIZE

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.length = 3
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0
        self.steps = 0

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self, apple):
        cur = self.get_head_position()
        x, y = self.direction
        new = (
            ((cur[0] + (x * GRIDSIZE)) % SCREEN_WIDTH),
            (cur[1] + (y * GRIDSIZE)) % SCREEN_HEIGHT,
        )
        if len(self.positions) > 2 and new in self.positions[2:]:
            self.reset()
            apple.randomize(self.positions)

        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 3
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0
        self.steps = 0

    def draw(self, surface):
        for p in self.positions:
            r = pygame.Rect((p[0], p[1]), (GRIDSIZE, GRIDSIZE))
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, BLACK, r, 1)


class Apple:
    def __init__(self, snake):
        self.position = (0, 0)
        self.color = RED
        self.randomize(snake.positions)

    def randomize(self, snake_positions):
        while True:
            new_position = (
                random.randint(0, GRID_WIDTH - 1) * GRIDSIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRIDSIZE,
            )
            if new_position not in snake_positions:
                break
        self.position = new_position

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (GRIDSIZE, GRIDSIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 1)


def draw_grid(surface):
    for y in range(0, int(GRID_HEIGHT)):
        for x in range(0, int(GRID_WIDTH)):
            r = pygame.Rect((x * GRIDSIZE, y * GRIDSIZE), (GRIDSIZE, GRIDSIZE))
            pygame.draw.rect(surface, BLACK, r)


def check_eat(snake, apple):
    if snake.get_head_position() == apple.position:
        snake.length += 1
        snake.score += 1
        apple.randomize(snake.positions)


# Game initialization
pygame.init()
pygame.font.init()
font = pygame.font.SysFont("monospace", 16)

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

surface = pygame.Surface(screen.get_size())
surface = surface.convert()
draw_grid(surface)

snake = Snake()
apple = Apple(snake)

scores = []
steps = []

while True:
    clock.tick(10)
    snake.move(apple)
    check_eat(snake, apple)
    draw_grid(surface)
    snake.draw(surface)
    apple.draw(surface)
    screen.blit(surface, (0, 0))

    text = font.render("Score {0}".format(snake.score), 1, (255, 255, 255))
    screen.blit(text, (5, 10))
    text = font.render("Steps {0}".format(snake.steps), 1, (255, 255, 255))
    screen.blit(text, (5, 30))
    pygame.display.update()

    scores.append(snake.score)
    snake.steps += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
