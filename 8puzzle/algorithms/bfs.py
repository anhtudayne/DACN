"""Breadth-First Search implementation for 8-puzzle"""
from collections import deque

def bfs_search(puzzle):
    """Returns (path from initial to goal, nodes explored) or (None, nodes explored)"""
    if not puzzle.is_solvable():
        return None, 0
        
    # Initialize with start state
    queue = deque([[puzzle.initial_state]])
    visited = {puzzle.get_state_string(puzzle.initial_state)}
    nodes_explored = 1
    
    while queue:
        path = queue.popleft()
        state = path[-1]
        
        if puzzle.is_goal(state):
            return path, nodes_explored
            
        for move in puzzle.get_possible_moves(state):
            try:
                new_state = puzzle.apply_move(state, move)
                state_string = puzzle.get_state_string(new_state)
                
                if state_string not in visited:
                    visited.add(state_string)
                    new_path = list(path)
                    new_path.append(new_state)
                    queue.append(new_path)
                    nodes_explored += 1
            except ValueError:
                continue  # Skip invalid moves
    
    return None, nodes_explored 