# Lab 3: Sudoku Solver

## Performed by: Zlatovcen Bogdan, group FAF-212

## Verified by: Elena Graur, asist. univ.

### Task 1: Implement a Solution for Solving Sudoku Puzzles Using Backtracking

For Task 1, I implemented the backtracking algorithm to solve Sudoku puzzles. The algorithm begins by locating the first empty cell in the grid and attempts to fill it with digits from 1 to 9. For each attempted number, it checks whether placing the number violates Sudoku's constraints in the corresponding row, column, or 3x3 subgrid. If a valid number is found, the algorithm recursively proceeds to solve the rest of the grid. If no valid number can be placed, it backtracks to the previous cell to try alternative numbers.

```python
def solve_backtracking(grid):
    empty = find_empty(grid)
    if not empty:
        return True  # Solved
    row, col = empty
    for num in '123456789':
        if is_valid(grid, num, (row, col)):
            grid[row][col] = num
            if solve_backtracking(grid):
                return True
            grid[row][col] = '*'  # Backtrack
    return False
```

### Task 2: Define Each Cell’s Domain and Implement Constraint Propagation to Eliminate Impossible Values for Each Cell

In Task 2, I defined each cell's domain by identifying all possible valid numbers that can occupy an empty cell without violating Sudoku's rules. Constraint propagation was implemented by iterating through each empty cell and eliminating numbers from its domain that already exist in the same row, column, or 3x3 subgrid. This reduction of possible values helps streamline the solving process by narrowing down the candidates for each cell.

```python
def get_domains(grid):
    domains = {}
    for i in range(9):
        for j in range(9):
            if grid[i][j] == '*':
                possible = set('123456789')
                possible -= set(grid[i])  # Remove numbers from the same row
                possible -= set(grid[r][j] for r in range(9))  # Remove numbers from the same column
                box_x = j // 3
                box_y = i // 3
                possible -= set(
                    grid[r][c]
                    for r in range(box_y*3, box_y*3 + 3)
                    for c in range(box_x*3, box_x*3 + 3)
                )  # Remove numbers from the same 3x3 subgrid
                domains[(i, j)] = possible
    return domains

def task2_constraint_propagation(grid):
    domains = get_domains(grid)
    print("Domains after initial Constraint Propagation:")
    for key in sorted(domains):
        print(f"Cell {key}: {sorted(domains[key])}")
```

### Task 3: Combine the Backtracking Algorithm with Constraint Propagation and Implement Forward Checking

For Task 3, I integrated forward checking with the backtracking algorithm to enhance efficiency. After assigning a number to a cell, forward checking updates the domains of all neighboring cells by removing the assigned number from their possible values. If any neighboring cell's domain becomes empty as a result, the algorithm recognizes a conflict and backtracks immediately, thus avoiding unnecessary deeper searches.

```python
def forward_checking(grid, domains, var, value):
    row, col = var
    local_domains = copy.deepcopy(domains)
    local_domains.pop(var)
    peers = get_peers(row, col)
    for peer in peers:
        if peer in local_domains:
            if value in local_domains[peer]:
                local_domains[peer].remove(value)
                if not local_domains[peer]:
                    return False, None
    return True, local_domains

def task3_backtracking_with_forward_checking(grid):
    grid_copy = copy.deepcopy(grid)
    domains = get_domains(grid_copy)
    if solve_backtracking_forward(grid_copy, domains):
        print("Solved Sudoku with Forward Checking:")
        print_grid(grid_copy)
    else:
        print("No solution exists for the provided Sudoku.")

def solve_backtracking_forward(grid, domains):
    if not domains:
        return True  # Solved
    var = min(domains, key=lambda v: len(domains[v]))  # MRV heuristic
    row, col = var
    for value in sorted(domains[var]):
        if is_valid(grid, value, var):
            grid[row][col] = value
            success, new_domains = forward_checking(grid, domains, var, value)
            if success:
                if solve_backtracking_forward(grid, new_domains):
                    return True
            grid[row][col] = '*'  # Backtrack
    return False
```

### Task 4: Implement a Heuristic Algorithm and Combine It with Constraint Propagation

In Task 4, I implemented the Minimum Remaining Value (MRV) heuristic to prioritize cells with the fewest possible valid numbers. This heuristic reduces the branching factor by tackling the most constrained cells first. Combined with constraint propagation, the solver efficiently narrows down the possibilities, leading to quicker resolution of the puzzle.

```python
def task4_heuristic_solver(grid):
    grid_copy = copy.deepcopy(grid)
    domains = get_domains(grid_copy)
    if solve_heuristic(grid_copy, domains):
        print("Solved Sudoku with Heuristic and Constraint Propagation:")
        print_grid(grid_copy)
    else:
        print("No solution exists for the provided Sudoku.")

def solve_heuristic(grid, domains):
    if not domains:
        return True  # Solved
    var = min(domains, key=lambda v: len(domains[v]))  # MRV heuristic
    row, col = var
    for value in sorted(domains[var]):
        if is_valid(grid, value, var):
            grid[row][col] = value
            new_domains = copy.deepcopy(domains)
            new_domains.pop(var)
            peers = get_peers(row, col)
            failure = False
            for peer in peers:
                if peer in new_domains:
                    if value in new_domains[peer]:
                        new_domains[peer].remove(value)
                        if not new_domains[peer]:
                            failure = True
                            break
            if not failure:
                if solve_heuristic(grid, new_domains):
                    return True
            grid[row][col] = '*'  # Backtrack
    return False
```

### Task 5: Generate Valid Sudoku Grids That Your Algorithm Will Solve

For Task 5, I developed a Sudoku puzzle generator that creates a fully solved grid and then removes a specified number of cells to form a puzzle. The generator ensures that each generated puzzle has a unique solution by verifying the number of possible solutions after each cell removal. This guarantees that the solver can effectively solve the generated puzzles without ambiguity.

```python
def generate_full_grid():
    grid = [['*' for _ in range(9)] for _ in range(9)]
    if fill_grid(grid):
        return grid
    else:
        print("Failed to generate a complete Sudoku grid.")
        return None

def fill_grid(grid):
    empty = find_empty(grid)
    if not empty:
        return True  # Complete
    row, col = empty
    numbers = list('123456789')
    random.shuffle(numbers)
    for num in numbers:
        if is_valid(grid, num, (row, col)):
            grid[row][col] = num
            if fill_grid(grid):
                return True
            grid[row][col] = '*'
    return False

def remove_cells(grid, attempts=40):
    grid_copy = copy.deepcopy(grid)
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    removed = 0
    for (row, col) in cells:
        if grid_copy[row][col] == '*':
            continue
        backup = grid_copy[row][col]
        grid_copy[row][col] = '*'
        grid_backup = copy.deepcopy(grid_copy)
        solutions = []
        count_solutions(grid_backup, solutions, 2)
        if len(solutions) != 1:
            grid_copy[row][col] = backup  # Revert if not unique
        else:
            removed += 1
        if removed >= attempts:
            break
    return grid_copy

def generate_sudoku():
    full_grid = generate_full_grid()
    if not full_grid:
        return None
    puzzle = remove_cells(full_grid, attempts=40)
    return puzzle

def task5_generate_sudoku():
    puzzle = generate_sudoku()
    if puzzle:
        print("Generated Sudoku Puzzle:")
        print_grid(puzzle)
    else:
        print("Failed to generate Sudoku puzzle.")
```

### Task 6: Handle Invalid Sudoku Puzzles by Determining Whether the Provided Grid Is Solvable

In Task 6, I implemented a validation mechanism to assess the solvability of a given Sudoku puzzle. The solver attempts to find all possible solutions up to two. If no solutions are found, the puzzle is deemed unsolvable. If exactly one solution exists, the puzzle has a unique solution. If multiple solutions are found, the puzzle has ambiguities. This validation ensures that only well-formed puzzles are considered solvable.

```python
def task6_handle_invalid_sudoku(grid):
    grid_copy = copy.deepcopy(grid)
    solutions = []
    count_solutions(grid_copy, solutions, 2)
    if len(solutions) == 0:
        print("The provided Sudoku puzzle is unsolvable.")
    elif len(solutions) == 1:
        print("The provided Sudoku puzzle has a unique solution.")
    else:
        print("The provided Sudoku puzzle has multiple solutions.")
```

### Task 7: Implement Constraint Propagation Algorithms to Improve Your Solution

For Task 7, I implemented the AC-3 (Arc Consistency Algorithm #3) constraint propagation algorithm to enhance the solver's efficiency. AC-3 systematically enforces consistency across all pairs of variables (cells) by eliminating values from a cell's domain that are inconsistent with its peers. By reducing the possible values early in the solving process, AC-3 minimizes the search space, leading to faster and more efficient puzzle resolution.

```python
def ac3(domains):
    """
    Implements the AC-3 algorithm for Constraint Propagation.
    Returns False if inconsistency is found, True otherwise.
    """
    queue = deque([(xi, xj) for xi in domains for xj in get_peers(xi[0], xi[1]) if xj in domains])
    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False
            for xk in get_peers(xi[0], xi[1]):
                if xk != xj and xk in domains:
                    queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    revised = False
    # If xj is assigned a value, remove it from xi's domain
    if len(domains[xj]) == 1:
        val = next(iter(domains[xj]))
        if val in domains[xi]:
            domains[xi].remove(val)
            revised = True
    return revised

def task7_constraint_propagation_ac3(grid):
    grid_copy = copy.deepcopy(grid)
    domains = get_domains(grid_copy)
    if not ac3(domains):
        print("Sudoku has no solution due to inconsistency after AC-3.")
        return
    if solve_with_ac3(grid_copy, domains):
        print("Solved Sudoku with AC-3 Constraint Propagation:")
        print_grid(grid_copy)
    else:
        print("No solution exists for the provided Sudoku after applying AC-3.")

def solve_with_ac3(grid, domains):
    if not domains:
        return True  # Solved
    var = min(domains, key=lambda v: len(domains[v]))  # MRV heuristic
    row, col = var
    for value in sorted(domains[var]):
        if is_valid(grid, value, var):
            grid[row][col] = value
            new_domains = copy.deepcopy(domains)
            new_domains.pop(var)
            # Remove the assigned value from peers
            for peer in get_peers(row, col):
                if peer in new_domains and value in new_domains[peer]:
                    new_domains[peer].remove(value)
                    if not new_domains[peer]:
                        break
            else:
                # Apply AC-3
                if ac3(new_domains):
                    if solve_with_ac3(grid, new_domains):
                        return True
            grid[row][col] = '*'  # Backtrack
    return False
```
