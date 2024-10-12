import pygame
import sys
import math
import heapq
import random

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 1000, 1000  # Large map size
ROWS, COLS = 50, 50  # Large grid size
CELL_SIZE = WIDTH // COLS
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ghost Avoidance Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)
YELLOW = (200, 200, 0)

# Directions
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Fonts
FONT = pygame.font.SysFont('Arial', 18)

# Global Variables for Scoring Info
CURRENT_SCORE = 0
PALLET_SCORE = 0
GHOST_DANGER = 0

# Transposition Table for memoization
transposition_table = {}

# Game Map Class
class GameMap:
    def __init__(self):
        self.walls = set()
        self.pallets = set()
        self.create_map()

    def create_map(self):
        # Create outer walls
        for x in range(COLS):
            self.walls.add((x, 0))
            self.walls.add((x, ROWS - 1))
        for y in range(ROWS):
            self.walls.add((0, y))
            self.walls.add((COLS - 1, y))

        # Generate walls in a less complex manner
        for x in range(2, COLS - 2, 4):
            for y in range(2, ROWS - 2, 4):
                # Create horizontal walls
                for i in range(-1, 2):
                    if 0 < x + i < COLS - 1 and 0 < y < ROWS - 1:
                        self.walls.add((x + i, y))
                # Create vertical walls
                for j in range(-1, 2):
                    if 0 < x < COLS - 1 and 0 < y + j < ROWS - 1:
                        self.walls.add((x, y + j))

        # Place pallets in open spaces
        for x in range(1, COLS - 1):
            for y in range(1, ROWS - 1):
                if (x, y) not in self.walls and random.random() < 0.3:
                    self.pallets.add((x, y))

    def draw(self, win):
        win.fill(BLACK)
        # Draw walls
        for wall in self.walls:
            x, y = wall
            pygame.draw.rect(win, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw pallets
        for pallet in self.pallets:
            x, y = pallet
            pygame.draw.circle(win, YELLOW, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 6)

# Agent Class
class Agent:
    def __init__(self, x, y):
        self.pos = (x, y)
        self.previous_positions = []

    def draw(self, win):
        x, y = self.pos
        pygame.draw.circle(win, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

# Ghost Class
class Ghost:
    def __init__(self, x, y):
        self.pos = (x, y)

    def move_towards(self, target, game_map):
        # A* pathfinding towards the agent
        path = a_star(self.pos, target, game_map, avoid_pallets=False)
        if len(path) > 1:
            self.pos = path[1]

    def draw(self, win):
        x, y = self.pos
        pygame.draw.circle(win, RED, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

# Game State Class
class GameState:
    def __init__(self, agent_pos, ghost_positions, pallets, depth=0, prev_positions=None):
        self.agent_pos = agent_pos
        self.ghost_positions = ghost_positions
        self.pallets = pallets
        self.depth = depth
        self.prev_positions = prev_positions if prev_positions is not None else []

    def is_terminal(self):
        # Game ends if no pallets left or agent is caught by a ghost
        return len(self.pallets) == 0 or self.agent_pos in self.ghost_positions

    def __hash__(self):
        return hash((self.agent_pos, self.ghost_positions, tuple(sorted(self.pallets))))

    def __eq__(self, other):
        return (self.agent_pos == other.agent_pos and
                self.ghost_positions == other.ghost_positions and
                self.pallets == other.pallets)

# A* Pathfinding Function
def a_star(start, goal, game_map, avoid_pallets=True):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        for dx, dy in DIRECTIONS:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in game_map.walls:
                continue
            if avoid_pallets and neighbor in game_map.pallets:
                continue
            if neighbor[0] < 0 or neighbor[0] >= COLS or neighbor[1] < 0 or neighbor[1] >= ROWS:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
    return []

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# MiniMax Algorithm with Alpha-Beta Pruning and Transposition Tables
def minimax(game_state, depth, alpha, beta, maximizingPlayer, game_map):
    global transposition_table
    if game_state in transposition_table and transposition_table[game_state][1] >= depth:
        return transposition_table[game_state][0]
    if depth == 0 or game_state.is_terminal():
        score = evaluate(game_state, game_map)
        transposition_table[game_state] = (score, depth)
        return score
    if maximizingPlayer:
        maxEval = -math.inf
        moves = get_valid_moves(game_state.agent_pos, game_map)
        moves = order_moves(game_state, moves, game_map)
        for move in moves:
            new_pallets = set(game_state.pallets)
            if move in new_pallets:
                new_pallets.remove(move)
            new_prev_positions = game_state.prev_positions[-4:] + [game_state.agent_pos]
            new_state = GameState(move, game_state.ghost_positions, frozenset(new_pallets), game_state.depth + 1, new_prev_positions)
            eval = minimax(new_state, depth - 1, alpha, beta, False, game_map)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Alpha-Beta Pruning
        transposition_table[game_state] = (maxEval, depth)
        return maxEval
    else:
        minEval = math.inf
        # Simulate ghosts moving towards the agent
        ghost_moves = ghost_possible_moves(game_state, game_map)
        for new_ghost_positions in ghost_moves:
            new_state = GameState(game_state.agent_pos, new_ghost_positions, game_state.pallets, game_state.depth + 1, game_state.prev_positions)
            eval = minimax(new_state, depth - 1, alpha, beta, True, game_map)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha-Beta Pruning
        transposition_table[game_state] = (minEval, depth)
        return minEval

def ghost_possible_moves(game_state, game_map):
    # Generate possible positions for all ghosts
    ghost_positions = list(game_state.ghost_positions)
    possible_positions = [get_valid_moves(pos, game_map) for pos in ghost_positions]
    # Generate combinations of ghost moves
    from itertools import product
    combinations = product(*possible_positions)
    # Limit the number of combinations to prevent performance issues
    limited_combinations = []
    for combo in combinations:
        limited_combinations.append(combo)
        if len(limited_combinations) >= 5:  # Adjust limit as needed
            break
    return limited_combinations

def get_valid_moves(pos, game_map):
    moves = []
    for dx, dy in DIRECTIONS:
        new_pos = (pos[0] + dx, pos[1] + dy)
        if 0 <= new_pos[0] < COLS and 0 <= new_pos[1] < ROWS and new_pos not in game_map.walls:
            moves.append(new_pos)
    return moves

def order_moves(game_state, moves, game_map):
    # Order moves based on heuristic evaluation
    scored_moves = []
    for move in moves:
        new_pallets = set(game_state.pallets)
        if move in new_pallets:
            new_pallets.remove(move)
        temp_state = GameState(move, game_state.ghost_positions, frozenset(new_pallets), prev_positions=game_state.prev_positions)
        score = evaluate(temp_state, game_map)
        scored_moves.append((score, move))
    scored_moves.sort(reverse=True)
    ordered_moves = [move for _, move in scored_moves]
    return ordered_moves

# Evaluation Function with Improved Scoring
def evaluate(game_state, game_map):
    global PALLET_SCORE, GHOST_DANGER
    # Pallet Score: Negative distance to the nearest pallet
    if game_state.pallets:
        distances = [heuristic(game_state.agent_pos, pallet) for pallet in game_state.pallets]
        min_pallet_distance = min(distances)
        PALLET_SCORE = -min_pallet_distance
    else:
        PALLET_SCORE = 1000  # Reward for collecting all pallets
    # Ghost Danger: Large negative value if too close to ghosts
    ghost_distances = [heuristic(game_state.agent_pos, ghost_pos) for ghost_pos in game_state.ghost_positions]
    min_ghost_distance = min(ghost_distances)
    if min_ghost_distance == 0:
        GHOST_DANGER = -10000  # Immediate danger
    else:
        GHOST_DANGER = -500 / min_ghost_distance  # The closer the ghost, the more negative
    # Loop Penalty: Penalize returning to recent positions
    loop_penalty = 0
    if game_state.agent_pos in game_state.prev_positions:
        loop_penalty = -100  # Increased penalty to discourage looping
    # Final Score
    score = PALLET_SCORE + GHOST_DANGER + loop_penalty
    return score

# Main Game Loop
def main():
    global CURRENT_SCORE, PALLET_SCORE, GHOST_DANGER, transposition_table
    clock = pygame.time.Clock()
    game_map = GameMap()
    # Ensure the agent starts in a non-wall position
    while True:
        agent_start_pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if agent_start_pos not in game_map.walls:
            break
    agent = Agent(*agent_start_pos)
    # Place 3 ghosts
    ghosts = []
    ghost_positions = set()
    while len(ghosts) < 3:
        ghost_pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if ghost_pos not in game_map.walls and ghost_pos != agent.pos and ghost_pos not in ghost_positions:
            ghosts.append(Ghost(*ghost_pos))
            ghost_positions.add(ghost_pos)
    running = True
    while running:
        clock.tick(10)  # Control the frame rate
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        transposition_table.clear()  # Clear transposition table for new turn

        # Get the best move from MiniMax Algorithm with iterative deepening
        agent.previous_positions.append(agent.pos)
        agent.previous_positions = agent.previous_positions[-4:]  # Keep last 4 positions
        game_state = GameState(agent.pos, tuple(ghost.pos for ghost in ghosts), frozenset(game_map.pallets), prev_positions=agent.previous_positions)
        best_move = agent.pos
        max_depth = 2  # Adjust based on performance
        try:
            for depth in range(1, max_depth + 1):
                best_score = -math.inf
                moves = get_valid_moves(agent.pos, game_map)
                moves = order_moves(game_state, moves, game_map)
                for move in moves:
                    new_pallets = set(game_map.pallets)
                    if move in new_pallets:
                        new_pallets.remove(move)
                    new_prev_positions = agent.previous_positions[-4:] + [agent.pos]
                    new_state = GameState(move, tuple(ghost.pos for ghost in ghosts), frozenset(new_pallets), prev_positions=new_prev_positions)
                    score = minimax(new_state, depth, -math.inf, math.inf, False, game_map)
                    if score > best_score:
                        best_score = score
                        best_move = move
        except KeyboardInterrupt:
            pass  # Allow early termination

        # Move the agent
        agent.pos = best_move
        # Eat pallet if present
        if agent.pos in game_map.pallets:
            game_map.pallets.remove(agent.pos)
            CURRENT_SCORE += 10  # Increase score
        # Move ghosts
        for ghost in ghosts:
            ghost.move_towards(agent.pos, game_map)
        # Check for collision after moving ghosts
        for ghost in ghosts:
            if ghost.pos == agent.pos:
                print("Game Over! You've been caught by a ghost!")
                running = False

        # Update the display
        game_map.draw(WIN)
        agent.draw(WIN)
        for ghost in ghosts:
            ghost.draw(WIN)

        # Display Scoring Information
        score_text = FONT.render(f"Score: {CURRENT_SCORE}", True, WHITE)
        pallet_text = FONT.render(f"Pallet Score: {PALLET_SCORE:.2f}", True, WHITE)
        ghost_text = FONT.render(f"Ghost Danger: {GHOST_DANGER:.2f}", True, WHITE)
        WIN.blit(score_text, (10, HEIGHT - 60))
        WIN.blit(pallet_text, (10, HEIGHT - 40))
        WIN.blit(ghost_text, (10, HEIGHT - 20))

        pygame.display.update()

        # Check if game is won
        if not game_map.pallets:
            print("Congratulations! You've collected all the pallets!")
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
