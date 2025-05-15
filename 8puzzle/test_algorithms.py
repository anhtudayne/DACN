"""
Test script for evaluating the correctness of various algorithms for 8-puzzle
"""
import time
from models.puzzle import Puzzle
from algorithms.simulated_annealing import simulated_annealing
from algorithms.stochastic_hill_climbing import stochastic_hill_climbing
from algorithms.astar import astar_search  # For comparison
from algorithms.genetic_algorithm import genetic_algorithm  # Thêm thuật toán Di truyền
from algorithms.andor_search import andor_graph_search  # Thuật toán And-Or Search
from algorithms.andor_po_search import partially_observable_andor_search  # Thuật toán And-Or Search cho môi trường quan sát một phần

def format_path(path):
    """Format path for display"""
    if not path:
        return "No solution found"
    return f"Solution found with {len(path)-1} steps"

def print_state(state):
    """Print a puzzle state in a readable format"""
    for row in state:
        print(row)
    print()

def run_test(initial_state, test_name="Test"):
    """Run a test with a specific initial state"""
    print(f"\n===== {test_name} =====")
    print("Initial State:")
    print_state(initial_state)
    
    # Create puzzle with the initial state
    puzzle = Puzzle(initial_state)
    
    if not puzzle.is_solvable():
        print("This puzzle is not solvable!")
        return
    
    # Test A* (as a reference since it's known to be correct)
    start_time = time.time()
    astar_path, astar_nodes = astar_search(puzzle)
    astar_time = time.time() - start_time
    
    # Test Simulated Annealing
    start_time = time.time()
    sa_path, sa_nodes = simulated_annealing(puzzle)
    sa_time = time.time() - start_time
    
    # Test Stochastic Hill Climbing
    start_time = time.time()
    stoch_path, stoch_nodes = stochastic_hill_climbing(puzzle)
    stoch_time = time.time() - start_time
    
    # Test Genetic Algorithm
    start_time = time.time()
    ga_path, ga_nodes = genetic_algorithm(puzzle, pop_size=200, max_generations=200, max_time=15, 
                                       tournament_size=5, crossover_rate=0.85, mutation_rate=0.15)
    ga_time = time.time() - start_time
    
    # Test And-Or Search (phiên bản cơ bản)
    start_time = time.time()
    andor_path, andor_nodes = andor_graph_search(puzzle, max_depth=20, max_time=10)
    andor_time = time.time() - start_time
    
    # Phiên bản nâng cao đã bị loại bỏ
    adv_andor_path, adv_andor_nodes = [], 0
    adv_andor_time = 0
    
    # Print results
    print("\nResults:")
    print(f"A* Search:               {format_path(astar_path)}, explored {astar_nodes} nodes in {astar_time:.4f}s")
    print(f"Simulated Annealing:     {format_path(sa_path)}, explored {sa_nodes} nodes in {sa_time:.4f}s")
    print(f"Stochastic Hill Climbing: {format_path(stoch_path)}, explored {stoch_nodes} nodes in {stoch_time:.4f}s")
    print(f"Genetic Algorithm:       {format_path(ga_path)}, explored {ga_nodes} nodes in {ga_time:.4f}s")
    print(f"And-Or Graph Search:     {format_path(andor_path)}, explored {andor_nodes} nodes in {andor_time:.4f}s")
    # Phiên bản nâng cao đã bị loại bỏ
    # print(f"Advanced And-Or Search:  {format_path(adv_andor_path)}, explored {adv_andor_nodes} nodes in {adv_andor_time:.4f}s")
    
    # Validate solution correctness for SA
    if sa_path:
        print("\nValidating Simulated Annealing solution...")
        is_valid = validate_solution(puzzle, sa_path)
        print(f"Simulated Annealing solution is {'valid' if is_valid else 'INVALID'}")
    
    # Validate solution correctness for Stochastic Hill Climbing
    if stoch_path:
        print("\nValidating Stochastic Hill Climbing solution...")
        is_valid = validate_solution(puzzle, stoch_path)
        print(f"Stochastic Hill Climbing solution is {'valid' if is_valid else 'INVALID'}")
    
    # Validate solution correctness for Genetic Algorithm
    if ga_path:
        print("\nValidating Genetic Algorithm solution...")
        is_valid = validate_solution(puzzle, ga_path)
        print(f"Genetic Algorithm solution is {'valid' if is_valid else 'INVALID'}")
        
    # Validate solution correctness for And-Or Graph Search
    if andor_path:
        print("\nValidating And-Or Graph Search solution...")
        is_valid = validate_solution(puzzle, andor_path)
        print(f"And-Or Graph Search solution is {'valid' if is_valid else 'INVALID'}")
        
    # Thêm kiểm tra cho Partially Observable And-Or Search
    start_time = time.time()
    po_andor_path, po_andor_nodes = partially_observable_andor_search(puzzle, max_time=15)
    po_andor_time = time.time() - start_time
    print(f"Partially Observable And-Or Search: {format_path(po_andor_path)}, explored {po_andor_nodes} nodes in {po_andor_time:.4f}s")
    
    if po_andor_path:
        print("\nValidating Partially Observable And-Or Search solution...")
        is_valid = validate_solution(puzzle, po_andor_path)
        print(f"Partially Observable And-Or Search solution is {'valid' if is_valid else 'INVALID'}")
        
    # Phiên bản nâng cao đã bị loại bỏ
    # Validate solution correctness for Advanced And-Or Search
    # if adv_andor_path:
    #     print("\nValidating Advanced And-Or Search solution...")
    #     is_valid = validate_solution(puzzle, adv_andor_path)
    #     print(f"Advanced And-Or Search solution is {'valid' if is_valid else 'INVALID'}")

def validate_solution(puzzle, path):
    """Validate that a solution path is correct"""
    if not path:
        return False
    
    # Check if the first state is the initial state
    if path[0] != puzzle.initial_state:
        print("Path does not start with the initial state")
        return False
    
    # Check if the last state is the goal state
    if not puzzle.is_goal(path[-1]):
        print("Path does not end with the goal state")
        return False
    
    # Check each move in the path
    for i in range(len(path) - 1):
        current_state = path[i]
        next_state = path[i + 1]
        
        # Try all possible moves from the current state
        valid_move = False
        for move in puzzle.get_possible_moves(current_state):
            try:
                new_state = puzzle.apply_move(current_state, move)
                if new_state == next_state:
                    valid_move = True
                    break
            except ValueError:
                continue
        
        if not valid_move:
            print(f"Invalid move detected at step {i+1}")
            print("Current state:")
            print_state(current_state)
            print("Next state:")
            print_state(next_state)
            return False
    
    return True

def main():
    """Run all tests"""
    # Test case 1: Simple puzzle (1 step)
    # 1 2 3
    # 4 5 6
    # 7 0 8
    test1 = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 0, 8]
    ]
    run_test(test1, "Test 1 - Simple (1 step)")
    
    # Test case 2: Medium difficulty
    # 1 2 3
    # 4 0 6
    # 7 5 8
    test2 = [
        [1, 2, 3],
        [4, 0, 6],
        [7, 5, 8]
    ]
    run_test(test2, "Test 2 - Medium")
    
    # Test case 3: Harder puzzle
    # 1 2 3
    # 5 0 6
    # 4 7 8
    test3 = [
        [1, 2, 3],
        [5, 0, 6],
        [4, 7, 8]
    ]
    run_test(test3, "Test 3 - Hard")
    
    # Test case 4: Complex puzzle
    # 8 1 3
    # 4 0 2
    # 7 6 5
    test4 = [
        [8, 1, 3],
        [4, 0, 2],
        [7, 6, 5]
    ]
    run_test(test4, "Test 4 - Complex")
    
    # Test case 5: Very complex puzzle
    # 7 2 4
    # 5 0 6
    # 8 3 1
    test5 = [
        [7, 2, 4],
        [5, 0, 6],
        [8, 3, 1]
    ]
    run_test(test5, "Test 5 - Very Complex")

if __name__ == "__main__":
    main()
