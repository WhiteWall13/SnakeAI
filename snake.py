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
        # self.direction = RIGHT  # Initial direction might not be necessary
        self.color = GREEN
        self.score = 0
        self.steps = 0
        # Initialize HamiltonianCycle with the start position
        self.hamiltonian_cycle = HamiltonianCycle(GRID_WIDTH, GRID_HEIGHT, self.positions[0], self.direction)


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
        # new = (
        #     ((cur[0] + (x * GRIDSIZE)) % SCREEN_WIDTH),
        #     (cur[1] + (y * GRIDSIZE)) % SCREEN_HEIGHT,
        # )
        new = self.hamiltonian_cycle.next_position(self.get_head_position())
        if len(self.positions) > 2 and new in self.positions[2:]:
            print("GAME OVER")
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


# class HamiltonianCycle:
#     def __init__(self, grid_width, grid_height):
#         self.grid_width = grid_width
#         self.grid_height = grid_height
#         self.path = self.generate_cycle()

#     def generate_cycle(self):
#         path = []
#         # Commence en haut à gauche et se déplace à droite jusqu'à la fin
#         for x in range(0, self.grid_width):
#             path.append((x * GRIDSIZE, 0))

#         # Commence les zigzags à partir de la droite vers la gauche, en évitant la première colonne
#         for y in range(1, self.grid_height):
#             if y % 2 == 1:
#                 # Descendre d'une ligne à l'extrême droite et se déplacer vers la gauche
#                 path.extend(
#                     [
#                         (x * GRIDSIZE, y * GRIDSIZE)
#                         for x in range(self.grid_width - 1, 0, -1)
#                     ]
#                 )
#             else:
#                 # Se déplacer vers la droite mais seulement jusqu'à la deuxième colonne (en évitant la première colonne)
#                 path.extend(
#                     [(x * GRIDSIZE, y * GRIDSIZE) for x in range(1, self.grid_width)]
#                 )

#         # Finalement, remonter par la première colonne
#         path.extend([(0, y * GRIDSIZE) for y in range(self.grid_height - 1, -1, -1)])

#         return path

#     def next_position(self, current_position):
#         # Trouver la position actuelle dans le chemin
#         index = self.path.index(current_position)
#         # Retourner la position suivante dans le chemin
#         return self.path[(index + 1) % len(self.path)]
    
class HamiltonianCycle:
    def __init__(self, grid_width, grid_height, start_position, direction):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.start_position = start_position
        self.path = self.generate_cycle(direction)

    def generate_cycle(self, current_direction):
        path = [self.start_position]
        # Prioriser la direction actuelle du serpent
        direction_order = [current_direction] + [d for d in [RIGHT, DOWN, LEFT, UP] if d != current_direction]
        move_attempts = 0

        while len(path) < self.grid_width * self.grid_height and move_attempts < len(direction_order):
            current_position = path[-1]
            x, y = current_position
            grid_x, grid_y = x // GRIDSIZE, y // GRIDSIZE

            for direction in direction_order:
                dx, dy = direction
                new_position = ((grid_x + dx) * GRIDSIZE, (grid_y + dy) * GRIDSIZE)

                if (0 <= new_position[0] < SCREEN_WIDTH and 0 <= new_position[1] < SCREEN_HEIGHT and new_position not in path):
                    path.append(new_position)
                    move_attempts = 0  # Réinitialiser le compteur d'essais
                    # Mettre à jour l'ordre de direction basé sur la direction actuelle
                    direction_order = [direction] + [d for d in [RIGHT, DOWN, LEFT, UP] if d != direction]
                    break
                else:
                    move_attempts += 1

        return path

    
    def recalculate_cycle(self, new_start_position, direction):
        self.start_position = new_start_position
        self.path = self.generate_cycle(direction)



    def next_position(self, current_position):
        # Find the current position in the path
        index = self.path.index(current_position)
        # Return the next position in the path
        return self.path[(index + 1) % len(self.path)]



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
        snake.hamiltonian_cycle.recalculate_cycle(snake.get_head_position(), snake.direction)


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
    clock.tick(100)
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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.turn(UP)
            elif event.key == pygame.K_DOWN:
                snake.turn(DOWN)
            elif event.key == pygame.K_LEFT:
                snake.turn(LEFT)
            elif event.key == pygame.K_RIGHT:
                snake.turn(RIGHT)
