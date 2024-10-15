# Lab 2: Searching Algorithms

## Performed by: Zlatovcen Bogdan, group FAF-212

## Verified by: Elena Graur, asist. univ.

### Task 1: Implement the MiniMax Algorithm with the Given Scoring Function

The minimax function implements the MiniMax algorithm with Alpha-Beta Pruning (Task 2). Pallet Score is calculated as the negative distance to the nearest pallet. The negative sign ensures that moving closer to a pallet increases the score. Ghost Danger is calculated as the negative inverse of the distance to the nearest ghost, scaled by -500. This makes the score more negative as the agent gets closer to a ghost. The total score is the sum of pallet_score and ghost_danger.

```python
def minimax(game_state, depth, alpha, beta, maximizingPlayer, game_map):
    if depth == 0 or game_state.is_terminal():
        score = evaluate(game_state, game_map)
        return score
    if maximizingPlayer:
        maxEval = -math.inf
        moves = get_valid_moves(game_state.agent_pos, game_map)
        for move in moves:
            new_pallets = set(game_state.pallets)
            if move in new_pallets:
                new_pallets.remove(move)
            new_state = GameState(move, game_state.ghost_positions, frozenset(new_pallets), game_state.depth + 1)
            eval = minimax(new_state, depth - 1, alpha, beta, False, game_map)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Alpha-Beta Pruning
        return maxEval
    else:
        minEval = math.inf
        # Simulate ghosts moving towards the agent
        new_ghost_positions = []
        for ghost_pos in game_state.ghost_positions:
            path = a_star(ghost_pos, game_state.agent_pos, game_map, avoid_pallets=False)
            if len(path) > 1:
                new_ghost_positions.append(path[1])
            else:
                new_ghost_positions.append(ghost_pos)
        new_state = GameState(game_state.agent_pos, tuple(new_ghost_positions), game_state.pallets, game_state.depth + 1)
        eval = minimax(new_state, depth - 1, alpha, beta, True, game_map)
        minEval = min(minEval, eval)
        beta = min(beta, eval)
        return minEval
```

### Task 2: Implement Alpha-Beta Pruning

Alpha-Beta Pruning is implemented in the minimax function by introducing the alpha and beta parameters. These parameters keep track of the best already explored options along the path to the root for both the maximizer and minimizer.

```python
def minimax(game_state, depth, alpha, beta, maximizingPlayer, game_map):
    # ... (same as in Task 1)
    if maximizingPlayer:
        maxEval = -math.inf
        # ... (code for maximizer)
        for move in moves:
            # ... (code for generating new state)
            eval = minimax(new_state, depth - 1, alpha, beta, False, game_map)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Alpha-Beta Pruning
        return maxEval
    else:
        minEval = math.inf
        # ... (code for minimizer)
        eval = minimax(new_state, depth - 1, alpha, beta, True, game_map)
        minEval = min(minEval, eval)
        beta = min(beta, eval)
        if beta <= alpha:
            break  # Alpha-Beta Pruning
        return minEval
```

### Task 3: Implement an Improved Scoring (Evaluation) Method for MiniMax

A penalty is added if the agent revisits recent positions to discourage looping.

The agent's previous positions are tracked to apply the loop penalty.

```python
class Agent:
    def __init__(self, x, y):
        self.pos = (x, y)
        self.previous_positions = []
```

The evaluation function includes the loop penalty.

```python
def evaluate(game_state, game_map):
    # ... (same as before)
    # Loop Penalty: Penalize returning to recent positions
    loop_penalty = 0
    if game_state.agent_pos in game_state.prev_positions:
        loop_penalty = -100  # Increased penalty to discourage looping
    # Final Score
    score = pallet_score + ghost_danger + loop_penalty
    return score
```

### Task 4: Add at Least One Improvement to the MiniMax Algorithm

Transposition tables store previously evaluated game states to avoid redundant calculations. Before evaluating a game state, the algorithm checks if it's in the transposition table, and if it is, and the stored depth is sufficient, it uses the stored score. This avoids recalculating the score for identical game states.

```python
# Global Transposition Table
transposition_table = {}

def minimax(game_state, depth, alpha, beta, maximizingPlayer, game_map):
    global transposition_table
    if game_state in transposition_table and transposition_table[game_state][1] >= depth:
        return transposition_table[game_state][0]
    # ... (rest of the minimax function)
    # Store the result in the transposition table
    transposition_table[game_state] = (score, depth)
    return score
```

### Task 5: Improve the Path Finding Algorithm for the Agent Using the A-Star Algorithm

The A\* algorithm is implemented in the a_star function.

```python
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
            x, y = neighbor
            if 0 <= x < COLS and 0 <= y < ROWS:
                if game_map.grid[y][x] == 1:
                    continue  # Wall
                if avoid_pallets and neighbor in game_map.pallets:
                    continue
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
    return []
```

In the minimax function, when simulating ghost movements, the A\* algorithm is used.

```python
# Simulate ghosts moving towards the agent
new_ghost_positions = []
for ghost_pos in game_state.ghost_positions:
    path = a_star(ghost_pos, game_state.agent_pos, game_map, avoid_pallets=False)
    if len(path) > 1:
        new_ghost_positions.append(path[1])
    else:
        new_ghost_positions.append(ghost_pos)
new_state = GameState(game_state.agent_pos, tuple(new_ghost_positions), game_state.pallets, game_state.depth + 1)
eval = minimax(new_state, depth - 1, alpha, beta, True, game_map)
```

### Task 6: Combine it with the Implemented Alpha-Beta Pruning Algorithm

In the minimax function, when simulating ghost movements and evaluating potential moves, both A\* pathfinding and Alpha-Beta Pruning are utilized.

```python
def minimax(game_state, depth, alpha, beta, maximizingPlayer, game_map):
    # ... (same as before)
    if maximizingPlayer:
        # ... (code for agent's moves)
    else:
        # Simulate ghosts moving towards the agent using A*
        new_ghost_positions = []
        for ghost_pos in game_state.ghost_positions:
            path = a_star(ghost_pos, game_state.agent_pos, game_map, avoid_pallets=False)
            if len(path) > 1:
                new_ghost_positions.append(path[1])
            else:
                new_ghost_positions.append(ghost_pos)
        new_state = GameState(game_state.agent_pos, tuple(new_ghost_positions), game_state.pallets, game_state.depth + 1)
        eval = minimax(new_state, depth - 1, alpha, beta, True, game_map)
        minEval = min(minEval, eval)
        beta = min(beta, eval)
        if beta <= alpha:
            break  # Alpha-Beta Pruning
        return minEval
```
