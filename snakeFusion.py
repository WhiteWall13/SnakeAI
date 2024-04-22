import pygame
import random
import heapq

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

class Node:
    def __init__(self, position):
        self.position = position
        self.distance = float('inf')
        self.previous = None

    def __lt__(self, other):
        return self.distance < other.distance

def get_free_spaces(position, body_positions):
    count = 0
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        neighbor_pos = (position[0] + dx * GRIDSIZE, position[1] + dy * GRIDSIZE)
        if (0 <= neighbor_pos[0] < SCREEN_WIDTH and 0 <= neighbor_pos[1] < SCREEN_HEIGHT) and (neighbor_pos not in body_positions):
            count += 1
    return count

from functools import lru_cache
@lru_cache(maxsize=None)
def simulate_future_mobility(position, body_positions, depth):

    if depth == 0:
        return 0

    max_spaces = 0
    x, y = position
    future_body_positions = set(body_positions)
    future_body_positions.add(position)

    # Évaluer chaque direction possible
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        next_pos = (x + dx * GRIDSIZE, y + dy * GRIDSIZE)
        if is_valid_position(next_pos, future_body_positions):
            local_spaces = get_free_spaces(next_pos, future_body_positions)
            # Recursion pour voir plus loin dans le futur
            future_result = simulate_future_mobility(next_pos, future_body_positions, depth - 1)
            max_spaces = max(max_spaces, local_spaces + future_result)

            future_body_positions.remove(next_pos)  # Retirez pour ne pas affecter les autres branches

    return max_spaces


def move_survival(snake, apple):
    head_x, head_y = snake.get_head_position()
    best_option = None
    best_score = -float('inf')

    depth = min(10, max(3, len(snake.positions) // 5))

    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        next_pos = (head_x + dx * GRIDSIZE, head_y + dy * GRIDSIZE)
        if is_valid_position(next_pos, snake.positions):
            free_spaces = get_free_spaces(next_pos, snake.positions)
            future_mobility = simulate_future_mobility(next_pos, snake.positions, depth)  # Profondeur ajustable selon les besoins
            score = free_spaces * 10 + future_mobility * 2  # Ajuster les poids selon la stratégie

            if score > best_score:
                best_score = score
                best_option = next_pos

    if best_option:
        snake.path.append(best_option)  # Planifiez le mouvement sans exécuter immédiatement
        # Après un mouvement survival, vérifiez si le chemin reste valide
        if not is_path_safe(snake.path, snake):
            update_path(snake, apple)  # Recalculer le chemin si nécessaire
        return False
    return True







def are_adjacent(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == GRIDSIZE

def get_adjacent_body_positions(snake):
    # Cette fonction devrait renvoyer toutes les positions adjacentes au serpent qui ne sont pas occupées par lui-même
    adjacent_positions = set()
    for body_part in snake.positions[1:]:
        x, y = body_part
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            adjacent_pos = (x + dx * GRIDSIZE, y + dy * GRIDSIZE)
            if is_valid_position(adjacent_pos, snake.positions) and adjacent_pos not in snake.positions:
                adjacent_positions.add(adjacent_pos)
    return adjacent_positions


def calculate_distance_to_body(position, body_positions):
    # Calculate the Manhattan distance from the position to the closest body part
    min_distance = float('inf')
    for body_part in body_positions:  # body_positions est déjà un ensemble de positions
        distance = abs(position[0] - body_part[0]) + abs(position[1] - body_part[1])
        min_distance = min(min_distance, distance)
    return min_distance





def is_valid_position(pos, body_positions):
    x, y = pos
    return (0 <= x < SCREEN_WIDTH) and (0 <= y < SCREEN_HEIGHT) and (pos not in body_positions)

def simulate_future_mobility(position, body_positions, depth):
    if depth == 0:
        return 0
    max_spaces = 0
    x, y = position
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        next_pos = (x + dx * GRIDSIZE, y + dy * GRIDSIZE)
        if is_valid_position(next_pos, body_positions):
            # Assurez-vous que future_body_positions est un set pour utiliser add
            future_body_positions = set(body_positions)  # Créez un nouveau set à partir de body_positions
            future_body_positions.add(next_pos)
            max_spaces = max(max_spaces, get_free_spaces(next_pos, future_body_positions) + simulate_future_mobility(next_pos, future_body_positions, depth - 1))
    return max_spaces


def update_snake_position(snake, next_pos):
    if len(snake.positions) >= snake.length:
        snake.positions.pop()
    snake.positions.insert(0, next_pos)


def evaluate_future_moves(position, snake):
    # This function needs to be implemented to simulate future moves
    # For now, return a simple heuristic based on available space
    return get_free_spaces(position, set(snake.positions))



def dijkstra(graph, start_pos, end_pos, body_positions):
    start = graph[start_pos]
    end = graph[end_pos]
    start.distance = 0
    queue = [(0, start)]  # La queue stocke une tuple de (distance, noeud)

    visited = set()
    
    while queue:
        current_distance, current = heapq.heappop(queue)
        if current.position in visited:
            continue
        visited.add(current.position)
        if current.position == end.position:
            break

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            x, y = current.position
            neighbor_pos = (x + dx * GRIDSIZE, y + dy * GRIDSIZE)
            if is_valid_position(neighbor_pos, body_positions):
                if neighbor_pos in visited:
                    continue
                neighbor = graph.get(neighbor_pos, Node(neighbor_pos))
                mobility_score = simulate_future_mobility(neighbor_pos, set(body_positions) | {neighbor_pos}, 3)
                new_dist = current_distance + 1 + mobility_score * 0.1  # Inclure la mobilité future dans le score
                if new_dist < neighbor.distance:
                    neighbor.distance = new_dist
                    neighbor.previous = current
                    heapq.heappush(queue, (new_dist, neighbor))

    # Reconstruire le chemin
    path = []
    while end.previous:
        path.insert(0, end.position)
        end = end.previous
    return path



class Snake:
    def __init__(self):
        self.length = 3
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.score = 0
        self.path = []
        self.color = GREEN  # Define the color attribute here.
    
    def reset(self):
        self.length = 3
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.score = 0
        self.path = []
    
    def get_head_position(self):
        return self.positions[0]
    
    
    def move(self):
        if self.path:
            next_pos = self.path.pop(0)
            # Vérifiez si la nouvelle tête est sur un segment du corps autre que l'ancienne queue (si la queue va bouger)
            if next_pos in self.positions[1:-1]:  # Ne vérifiez pas l'ancienne queue
                return True
            if len(self.positions) >= self.length:
                self.positions.pop()  # Enlève l'ancienne queue
            self.positions.insert(0, next_pos)  # Ajoute la nouvelle tête
        return False

    
    def grow(self):
        self.length += 1
    
    def draw(self, surface):
        # Draw the path first
        for p in self.path:
            rect = pygame.Rect((p[0], p[1]), (GRIDSIZE, GRIDSIZE))
            pygame.draw.rect(surface, (0, 0, 255), rect)  # Draw in blue

        # Draw the snake body
        for p in self.positions:
            rect = pygame.Rect((p[0], p[1]), (GRIDSIZE, GRIDSIZE))
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

    
    def move_anyway(self):
        head_x, head_y = self.get_head_position()
        possible_directions = [(head_x + dx * GRIDSIZE, head_y + dy * GRIDSIZE)
                               for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]]
        
        # Filter out positions that would collide with the snake's body
        possible_directions = [pos for pos in possible_directions if pos not in self.positions]
        
        # If there's nowhere to move (completely trapped), reset the game
        if not possible_directions:
            return True

        # Choose a random direction to move that does not result in a collision
        next_pos = random.choice(possible_directions)
        self.positions.pop()
        self.positions.insert(0, next_pos)
        return False

class Apple:
    def __init__(self):
        self.color = RED  # Define the color attribute for the apple
        self.randomize(snake.positions)  # Make sure this line comes after the color definition
    
    def randomize(self, snake_positions):
        while True:
            new_position = (random.randint(0, GRID_WIDTH - 1) * GRIDSIZE, random.randint(0, GRID_HEIGHT - 1) * GRIDSIZE)
            if new_position not in snake_positions:
                self.position = new_position
                break
    
    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (GRIDSIZE, GRIDSIZE))
        pygame.draw.rect(surface, self.color, r)  # Now self.color is defined
        pygame.draw.rect(surface, BLACK, r, 1)


def check_collision(snake, apple):
    if snake.get_head_position() == apple.position:
        snake.grow()
        snake.score += 1  # Augmenter le score quand le serpent mange une pomme
        apple.randomize(snake.positions)  # Placez une nouvelle pomme
        update_path(snake, apple)  # Recalculez le chemin après la croissance
        return True
    return False


def update_path(snake, apple):
    body_positions = set(snake.positions)
    graph = {((x * GRIDSIZE), (y * GRIDSIZE)): Node(((x * GRIDSIZE), (y * GRIDSIZE))) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)}
    initial_path = dijkstra(graph, snake.get_head_position(), apple.position, body_positions)

    if is_path_safe(initial_path, snake):
        snake.path = initial_path
    else:
        snake.path = calculate_safe_path(graph, snake, apple, body_positions)



def is_path_safe(path, snake):
    # Simuler le mouvement du serpent le long du chemin pour vérifier les issues potentielles
    simulated_positions = list(snake.positions)
    for pos in path:
        if not simulate_future_mobility(pos, simulated_positions, 3):  # Profondeur de simulation arbitraire
            return False
        simulated_positions.insert(0, pos)  # Simuler le mouvement
        if len(simulated_positions) > snake.length:
            simulated_positions.pop()
    return True

def calculate_safe_path(graph, snake, apple, body_positions):
    # Implémenter une logique pour recalculer un chemin sûr
    # Ceci est un exemple simplifié, des heuristiques ou des modifications de l'algorithme pourraient être nécessaires
    return dijkstra(graph, snake.get_head_position(), apple.position, body_positions - {snake.positions[-1]})


def reset_game():
    snake.reset()
    apple.randomize(snake.positions)
    update_path(snake, apple)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
surface = pygame.Surface(screen.get_size()).convert()
pygame.font.init()
font = pygame.font.SysFont("monospace", 16)

snake = Snake()
apple = Apple()
update_path(snake, apple)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if not snake.path:
        if not move_survival(snake, apple):  # Si le serpent est capable de bouger
            update_path(snake, apple)  # Tentez de recalculer le chemin
        else:
            reset_game()  # Si le serpent est complètement bloqué, réinitialiser le jeu
        continue

    moved = snake.move()
    if moved:  # Si le serpent se heurte à lui-même
        reset_game()

    if check_collision(snake, apple):
        update_path(snake, apple)  # Assurez-vous de mettre à jour après avoir mangé et possiblement grandi
        continue

    surface.fill(BLACK)
    snake.draw(surface)
    apple.draw(surface)
    screen.blit(surface, (0, 0))
    text = font.render(f"Score {snake.score}", True, (255, 255, 255))
    screen.blit(text, (5, 10))
    pygame.display.update()
    clock.tick(100)