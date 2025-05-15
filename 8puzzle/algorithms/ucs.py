"""Uniform Cost Search implementation for 8-puzzle"""
import heapq

class Node:
    def __init__(self, state, parent=None, cost=0):
        self.state = state
        self.parent = parent
        self.cost = cost    # Path cost from start
        
    def __lt__(self, other):
        return self.cost < other.cost
        
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

def ucs_search(puzzle):
    """Returns (path from initial to goal, nodes explored) or (None, nodes explored)"""
    if not puzzle.is_solvable():
        return None, 0
        
    start_node = Node(puzzle.initial_state)
    frontier = []
    heapq.heappush(frontier, start_node)
    
    visited = {puzzle.get_state_string(start_node.state): 0}
    nodes_explored = 1
    
    while frontier:
        current = heapq.heappop(frontier)
        current_state_str = puzzle.get_state_string(current.state)
        
        if puzzle.is_goal(current.state):
            path = []
            while current:
                path.append(current.state)
                current = current.parent
            return path[::-1], nodes_explored
            
        # Skip if we've found a better path to this state
        if current.cost > visited[current_state_str]:
            continue
            
        for move in puzzle.get_possible_moves(current.state):
            try:
                new_state = puzzle.apply_move(current.state, move)
                new_cost = current.cost + 1
                state_string = puzzle.get_state_string(new_state)
                
                if state_string not in visited or new_cost < visited[state_string]:
                    visited[state_string] = new_cost
                    new_node = Node(new_state, current, new_cost)
                    heapq.heappush(frontier, new_node)
                    nodes_explored += 1
            except ValueError:
                continue  # Skip invalid moves
    
    return None, nodes_explored 