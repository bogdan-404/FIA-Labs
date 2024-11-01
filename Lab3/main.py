# main.py

import copy
from collections import deque
import random

def read_grid():
    """
    Reads a Sudoku grid from user input.
    The user can input the entire grid at once, separated by newlines.
    Each line should have exactly 9 characters (digits 1-9 or '*').
    Returns the grid as a 2D list.
    """
    grid = []
    print("Enter the entire Sudoku grid. You can paste all 9 lines at once or enter them one by one.")
    print("Use digits 1-9 for filled cells and '*' for empty cells.")
    print("Example input (each row on a new line):")
    print("53**7****")
    print("6**195***")
    print("*98****6*")
    print("8***6***3")
    print("4**8*3**1")
    print("7***2***6")
    print("*6****28*")
    print("***419**5")
    print("****8**79")
    print("\nPlease enter the Sudoku grid:")
    
    while len(grid) < 9:
        try:
            line = input().strip()
            if not line:
                continue  # Skip empty lines
            lines = line.split()
            for ln in lines:
                if len(grid) >= 9:
                    break
                if len(ln) != 9 or not all(c.isdigit() or c == '*' for c in ln):
                    print("Invalid input detected. Each row must have exactly 9 characters (digits 1-9 or '*'). Please re-enter.")
                    grid = []
                    break
                grid.append(list(ln))
        except EOFError:
            break  # End of input
    if len(grid) != 9:
        print("Insufficient rows entered. Please ensure you enter exactly 9 rows.")
        return read_grid()
    return grid

def print_grid(grid):
    """
    Prints the Sudoku grid in a readable format.
    Empty cells are represented by '.' for clarity.
    """
    for i, row in enumerate(grid):
        row_str = ''
        for j, num in enumerate(row):
            row_str += num if num != '*' else '.'
            if (j + 1) % 3 == 0 and j < 8:
                row_str += ' | '
            else:
                row_str += ' '
        print(row_str)
        if (i + 1) % 3 == 0 and i < 8:
            print("- " * 11)

def generate_full_grid():
    """
    Generates a complete Sudoku grid using backtracking.
    Returns the completed grid as a 2D list.
    """
    grid = [['*' for _ in range(9)] for _ in range(9)]
    if fill_grid(grid):
        return grid
    else:
        print("Failed to generate a complete Sudoku grid.")
        return None

def fill_grid(grid):
    """
    Helper function to fill the grid recursively.
    """
    empty = find_empty(grid)
    if not empty:
        return True  # Grid is complete
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
    """
    Removes a number of cells from the grid to create a puzzle.
    The number of attempts determines how many cells to remove.
    Ensures that the puzzle has a unique solution.
    """
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

def count_solutions(grid, solutions, limit):
    """
    Counts the number of solutions for a given Sudoku grid.
    Stops counting after reaching the limit.
    """
    if len(solutions) >= limit:
        return
    empty = find_empty(grid)
    if not empty:
        solutions.append(copy.deepcopy(grid))
        return
    row, col = empty
    for num in '123456789':
        if is_valid(grid, num, (row, col)):
            grid[row][col] = num
            count_solutions(grid, solutions, limit)
            grid[row][col] = '*'

def generate_sudoku():
    """
    Generates a Sudoku puzzle by creating a full grid and then removing cells.
    Returns the puzzle grid as a 2D list.
    """
    full_grid = generate_full_grid()
    if not full_grid:
        return None
    puzzle = remove_cells(full_grid, attempts=40)
    return puzzle

def find_empty(grid):
    """
    Finds an empty cell in the grid.
    Returns a tuple (row, col) or None if the grid is full.
    """
    for i in range(9):
        for j in range(9):
            if grid[i][j] == '*':
                return (i, j)
    return None

def is_valid(grid, num, pos):
    """
    Checks whether it's valid to place num at position pos in the grid.
    pos is a tuple (row, col).
    """
    row, col = pos
    # Check row
    for j in range(9):
        if grid[row][j] == num and j != col:
            return False
    # Check column
    for i in range(9):
        if grid[i][col] == num and i != row:
            return False
    # Check 3x3 box
    box_x = col // 3
    box_y = row // 3
    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x*3, box_x*3 + 3):
            if grid[i][j] == num and (i, j) != pos:
                return False
    return True

def task1_backtracking_solver(grid):
    """
    Task 1: Solves the Sudoku using backtracking.
    """
    grid_copy = copy.deepcopy(grid)
    if solve_backtracking(grid_copy):
        print("Solved Sudoku:")
        print_grid(grid_copy)
    else:
        print("No solution exists for the provided Sudoku.")

def solve_backtracking(grid):
    """
    Solves the Sudoku puzzle using backtracking.
    Returns True if a solution is found, False otherwise.
    """
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

def get_domains(grid):
    """
    For each cell, defines its domain (possible values).
    Returns a dictionary with keys as (row, col) and values as sets of possible numbers.
    """
    domains = {}
    for i in range(9):
        for j in range(9):
            if grid[i][j] == '*':
                possible = set('123456789')
                # Remove numbers from the same row
                possible -= set(grid[i])
                # Remove numbers from the same column
                possible -= set(grid[r][j] for r in range(9))
                # Remove numbers from the same box
                box_x = j // 3
                box_y = i // 3
                possible -= set(
                    grid[r][c]
                    for r in range(box_y*3, box_y*3 + 3)
                    for c in range(box_x*3, box_x*3 + 3)
                )
                domains[(i, j)] = possible
    return domains

def task2_constraint_propagation(grid):
    """
    Task 2: Defines each cell’s domain and implements Constraint Propagation to eliminate impossible values.
    """
    domains = get_domains(grid)
    print("Domains after initial Constraint Propagation:")
    for key in sorted(domains):
        print(f"Cell {key}: {sorted(domains[key])}")

def forward_checking(grid, domains, var, value):
    """
    Implements forward checking by updating the domains after assigning value to var.
    Returns False if a domain is emptied, True otherwise along with the updated domains.
    """
    row, col = var
    # Create a copy of domains to modify
    local_domains = copy.deepcopy(domains)
    local_domains.pop(var)
    # Remove value from peers
    peers = get_peers(row, col)
    for peer in peers:
        if peer in local_domains:
            if value in local_domains[peer]:
                local_domains[peer].remove(value)
                if not local_domains[peer]:
                    return False, None
    return True, local_domains

def get_peers(row, col):
    """
    Returns a set of peer coordinates for a given cell.
    """
    peers = set()
    for j in range(9):
        if j != col:
            peers.add((row, j))
    for i in range(9):
        if i != row:
            peers.add((i, col))
    box_x = col // 3
    box_y = row // 3
    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x*3, box_x*3 + 3):
            if (i, j) != (row, col):
                peers.add((i, j))
    return peers

def task3_backtracking_with_forward_checking(grid):
    """
    Task 3: Combines Backtracking with Constraint Propagation and implements Forward Checking.
    """
    grid_copy = copy.deepcopy(grid)
    domains = get_domains(grid_copy)
    if solve_backtracking_forward(grid_copy, domains):
        print("Solved Sudoku with Forward Checking:")
        print_grid(grid_copy)
    else:
        print("No solution exists for the provided Sudoku.")

def solve_backtracking_forward(grid, domains):
    """
    Solves the Sudoku using backtracking with forward checking.
    """
    if not domains:
        return True  # Solved
    # Select the variable with the smallest domain (MRV heuristic)
    var = min(domains, key=lambda v: len(domains[v]))
    row, col = var
    for value in sorted(domains[var]):
        if is_valid(grid, value, var):
            grid[row][col] = value
            # Forward checking
            success, new_domains = forward_checking(grid, domains, var, value)
            if success:
                if solve_backtracking_forward(grid, new_domains):
                    return True
            grid[row][col] = '*'  # Backtrack
    return False

def task4_heuristic_solver(grid):
    """
    Task 4: Implements a heuristic algorithm (MRV) combined with Constraint Propagation.
    """
    grid_copy = copy.deepcopy(grid)
    domains = get_domains(grid_copy)
    if solve_heuristic(grid_copy, domains):
        print("Solved Sudoku with Heuristic and Constraint Propagation:")
        print_grid(grid_copy)
    else:
        print("No solution exists for the provided Sudoku.")

def solve_heuristic(grid, domains):
    """
    Solves the Sudoku using MRV heuristic and Constraint Propagation.
    """
    if not domains:
        return True  # Solved
    # MRV heuristic: choose the variable with the fewest possible values
    var = min(domains, key=lambda v: len(domains[v]))
    row, col = var
    for value in sorted(domains[var]):
        if is_valid(grid, value, var):
            grid[row][col] = value
            # Constraint Propagation
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
    """
    Revises the domain of xi to satisfy arc consistency with xj.
    For Sudoku, if xj has only one possible value, remove that value from xi's domain.
    Returns True if the domain of xi was revised, False otherwise.
    """
    revised = False
    # If xj is assigned a value, remove it from xi's domain
    if len(domains[xj]) == 1:
        val = next(iter(domains[xj]))
        if val in domains[xi]:
            domains[xi].remove(val)
            revised = True
    return revised

def task7_constraint_propagation_ac3(grid):
    """
    Task 7: Implements the AC-3 Constraint Propagation algorithm to improve the solution.
    """
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
    """
    Solves the Sudoku using backtracking enhanced with AC-3 Constraint Propagation.
    """
    if not domains:
        return True  # Solved
    # MRV heuristic
    var = min(domains, key=lambda v: len(domains[v]))
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

def task5_generate_sudoku():
    """
    Task 5: Generates a valid Sudoku grid that the algorithm can solve.
    """
    puzzle = generate_sudoku()
    if puzzle:
        print("Generated Sudoku Puzzle:")
        print_grid(puzzle)
    else:
        print("Failed to generate Sudoku puzzle.")

def task6_handle_invalid_sudoku(grid):
    """
    Task 6: Handles invalid Sudoku puzzles by determining whether the provided grid is solvable.
    """
    grid_copy = copy.deepcopy(grid)
    solutions = []
    count_solutions(grid_copy, solutions, 2)
    if len(solutions) == 0:
        print("The provided Sudoku puzzle is unsolvable.")
    elif len(solutions) == 1:
        print("The provided Sudoku puzzle has a unique solution.")
    else:
        print("The provided Sudoku puzzle has multiple solutions.")

def task_menu(grid):
    """
    Displays the task menu and handles user selection.
    """
    while True:
        print("\nChoose a task to execute:")
        print("1. Task 1: Backtracking Solver")
        print("2. Task 2: Constraint Propagation")
        print("3. Task 3: Backtracking with Forward Checking")
        print("4. Task 4: Heuristic Solver with Constraint Propagation")
        print("5. Task 5: Generate Sudoku Puzzle")
        print("6. Task 6: Validate Sudoku Puzzle")
        print("7. Task 7: AC-3 Constraint Propagation")
        print("0. Return to Main Menu")
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            task1_backtracking_solver(grid)
        elif choice == '2':
            task2_constraint_propagation(grid)
        elif choice == '3':
            task3_backtracking_with_forward_checking(grid)
        elif choice == '4':
            task4_heuristic_solver(grid)
        elif choice == '5':
            task5_generate_sudoku()
        elif choice == '6':
            task6_handle_invalid_sudoku(grid)
        elif choice == '7':
            task7_constraint_propagation_ac3(grid)
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please select a valid option.")

def main_menu():
    """
    Displays the main menu and handles user selection between generating or inputting a Sudoku puzzle.
    """
    while True:
        print("\nSudoku Solver Laboratory Work")
        print("1. Generate a Sudoku Puzzle")
        print("2. Input a Sudoku Puzzle")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            puzzle = generate_sudoku()
            if puzzle:
                print("\nGenerated Sudoku Puzzle:")
                print_grid(puzzle)
                task_menu(puzzle)
        elif choice == '2':
            grid = read_grid()
            print("\nInput Sudoku Puzzle:")
            print_grid(grid)
            task_menu(grid)
        elif choice == '0':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()
