"""Thuật toán Tìm kiếm Chùm tia (Beam Search) cho bài toán 8-puzzle"""
from .heuristics import manhattan_distance
import heapq

class Node:
    def __init__(self, state, parent=None, move=None, g=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.g = g  # Cost so far
        self.h = 0  # Heuristic value
        self.f = 0  # f = g + h
        
    def __lt__(self, other):
        return self.f < other.f
        
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

def beam_search(puzzle, beam_width=3, heuristic_func=manhattan_distance):
    
    if not puzzle.is_solvable():
        return None, 0
        
    initial_node = Node(puzzle.initial_state)
    initial_node.h = heuristic_func(initial_node.state, puzzle.goal_state)
    initial_node.f = initial_node.g + initial_node.h
    
    if puzzle.is_goal(initial_node.state):
        return [initial_node.state], 1
    
    beam = [initial_node]
    
    visited = {puzzle.get_state_string(initial_node.state)}
    
    nodes_explored = 1
    
    while beam:
        all_successors = []
        
        for node in beam:
            possible_moves = puzzle.get_possible_moves(node.state)
            
            for move in possible_moves:
                try:
                    new_state = puzzle.apply_move(node.state, move)
                    state_str = puzzle.get_state_string(new_state)
                    
                    if state_str in visited:
                        continue
                    
                    new_node = Node(new_state, node, move, node.g + 1)
                    new_node.h = heuristic_func(new_state, puzzle.goal_state)
                    new_node.f = new_node.g + new_node.h
                    
                    if puzzle.is_goal(new_state):
                        path = []
                        current = new_node
                        while current:
                            path.append(current.state)
                            current = current.parent
                        return path[::-1], nodes_explored + 1
                    
                    all_successors.append(new_node)
                    visited.add(state_str)
                    nodes_explored += 1
                    
                except ValueError:
                    continue  # Skip invalid moves
        
        if not all_successors:
            return None, nodes_explored
        
        beam = heapq.nsmallest(beam_width, all_successors)
    
    return None, nodes_explored
