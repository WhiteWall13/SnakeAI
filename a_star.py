
import pygame
import random
import heapq

# Define the colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid, start, goal, snake_positions):
    directions = [DOWN, RIGHT, UP, LEFT]  # DOWN, RIGHT, UP, LEFT
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    open_set = []

    heapq.heappush(open_set, (fscore[start], start))
    
    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        close_set.add(current)
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT:
                if grid[neighbor[1]][neighbor[0]] == 1:  # Position is blocked by the snake's body
                    continue
                if neighbor in close_set:
                    continue

                tentative_g_score = gscore[current] + 1  # Every step has a cost of 1
                if tentative_g_score < gscore.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (fscore[neighbor], neighbor))

    return []  # If no path is found


class Snake:
    def __init__(self):
        self.length = 3
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0
        self.steps = 0
        self.path = []  # Ajout de l'initialisation de path ici


    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point
    
    
    def move(self, apple, grid):
        update_grid(grid, self.positions)  # Leave the last segment free since it will be vacated
        start = (self.get_head_position()[0] // GRIDSIZE, self.get_head_position()[1] // GRIDSIZE)
        goal = (apple.position[0] // GRIDSIZE, apple.position[1] // GRIDSIZE)
        self.path = a_star_search(grid, start, goal, self.positions)
        
        if self.path:
            next_step = self.path[0]  # Prenez le premier pas du chemin
            new_head_position = (next_step[0] * GRIDSIZE, next_step[1] * GRIDSIZE)

            # Vérifiez si la nouvelle position est sur le corps du serpent
            if new_head_position in self.positions[:-1]:
                print("Collision detected, recalculating path.")
                # Corriger les indices ici
                head_pos = self.get_head_position()
                head_grid_x = head_pos[0] // GRIDSIZE
                head_grid_y = head_pos[1] // GRIDSIZE
                apple_grid_x = apple.position[0] // GRIDSIZE
                apple_grid_y = apple.position[1] // GRIDSIZE
                self.path = a_star_search(grid, (head_grid_x, head_grid_y), (apple_grid_x, apple_grid_y), self.positions)
                return  # Skip the move for this turn or handle differently
            else:
                # Continue avec le mouvement
                self.positions.insert(0, new_head_position)
                if len(self.positions) > self.length:
                    self.positions.pop()

                # Gestion de la pomme
                if new_head_position == apple.position:
                    self.length += 1
                    apple.randomize(self.positions)
        else:
            print("No path found. Game over or trying an alternative strategy.")

    def reset(self):
        self.length = 3
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0
        self.steps = 0

    def draw(self, surface):
        # Dessiner le serpent
        for p in self.positions:
            r = pygame.Rect((p[0], p[1]), (GRIDSIZE, GRIDSIZE))
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, BLACK, r, 1)

        # Dessiner le chemin en bleu
        if self.path:
            for step in self.path:
                r = pygame.Rect((step[0] * GRIDSIZE, step[1] * GRIDSIZE), (GRIDSIZE, GRIDSIZE))
                pygame.draw.rect(surface, BLUE, r)



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
        
def update_grid(grid, snake_positions):
    # Initialiser toute la grille à 0
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            grid[y][x] = 0

    # Marquer le corps du serpent comme obstacles
    for pos in snake_positions[:-1]:  # Excluez la queue si le serpent va se déplacer
        grid[pos[1] // GRIDSIZE][pos[0] // GRIDSIZE] = 1
        

def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("monospace", 16)
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    snake = Snake()
    apple = Apple(snake)
    
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    

    while True:
        snake.move(apple, grid)
        check_eat(snake, apple)
        
        screen.fill(BLACK)
        snake.draw(screen)
        apple.draw(screen)

        # Mettre à jour le score et les étapes ici avant l'update de l'écran
        text_score = font.render("Score {0}".format(snake.score), 1, (255, 255, 255))
        screen.blit(text_score, (5, 10))
        text_steps = font.render("Steps {0}".format(snake.steps), 1, (255, 255, 255))
        screen.blit(text_steps, (5, 30))
        
        pygame.display.update()
        clock.tick(100)

        snake.steps += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return


if __name__ == "__main__":
    main()
