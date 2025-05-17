"""Depth-First Search implementation for 8-puzzle"""

def dfs_search(puzzle, max_depth=200):
    
    if not puzzle.is_solvable():
        return None, 0
        
    stack = [[puzzle.initial_state]]
    visited = {puzzle.get_state_string(puzzle.initial_state)}
    nodes_explored = 1
    
    while stack:
        path = stack.pop()
        state = path[-1]
        
        if puzzle.is_goal(state):
            return path, nodes_explored
            
        if len(path) > max_depth:
            continue
            
        for move in puzzle.get_possible_moves(state):
            try:
                new_state = puzzle.apply_move(state, move)
                state_string = puzzle.get_state_string(new_state)
                
                if state_string not in visited:
                    visited.add(state_string)
                    new_path = list(path)
                    new_path.append(new_state)
                    stack.append(new_path)
                    nodes_explored += 1
            except ValueError:
                continue 
    
    return None, nodes_explored
