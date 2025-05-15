"""A* Search implementation for 8-puzzle"""
import heapq
from .heuristics import manhattan_distance

class Node:
    def __init__(self, state, parent=None, move=None, g=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.g = g      # Cost from start to current node
        self.h = 0      # Heuristic value (Manhattan distance)
        self.f = 0      # Total cost (f = g + h)
        
    def __lt__(self, other):
        return self.f < other.f
        
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

def astar_search(puzzle):
    """Returns (path from initial to goal, nodes explored) or (None, nodes explored)"""
    if not puzzle.is_solvable():
        return None, 0
        
    start_node = Node(puzzle.initial_state)
    start_node.h = manhattan_distance(start_node.state, puzzle.goal_state)
    start_node.f = start_node.g + start_node.h
    
    frontier = []
    heapq.heappush(frontier, start_node)
    
    # Track both cost and visited states
    cost_so_far = {puzzle.get_state_string(start_node.state): 0}
    visited = {puzzle.get_state_string(start_node.state)}
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
        if current_state_str in visited and current.g > cost_so_far[current_state_str]:
            continue
            
        for move in puzzle.get_possible_moves(current.state):
            try:
                new_state = puzzle.apply_move(current.state, move)
                new_cost = current.g + 1
                state_string = puzzle.get_state_string(new_state)
                
                if state_string not in cost_so_far or new_cost < cost_so_far[state_string]:
                    cost_so_far[state_string] = new_cost
                    visited.add(state_string)
                    new_node = Node(new_state, current, move, new_cost)
                    new_node.h = manhattan_distance(new_state, puzzle.goal_state)
                    new_node.f = new_node.g + new_node.h
                    heapq.heappush(frontier, new_node)
                    nodes_explored += 1
                    
            except ValueError:
                continue  # Skip invalid moves
    
    return None, nodes_explored 