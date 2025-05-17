"""Greedy Search implementation for 8-puzzle"""
import heapq
from .heuristics import manhattan_distance

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.h = 0      # Giá trị heuristic (khoảng cách Manhattan)
        
    def __lt__(self, other):
        return self.h < other.h
        
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

def greedy_search(puzzle):
   
    if not puzzle.is_solvable():
        return None, 0
    # Khởi tạo nút bắt đầu
    start_node = Node(puzzle.initial_state)
    start_node.h = manhattan_distance(start_node.state, puzzle.goal_state)
    
    # Hàng đợi ưu tiên (dựa trên giá trị heuristic)
    frontier = []
    heapq.heappush(frontier, start_node)
    visited = {puzzle.get_state_string(start_node.state)}
    nodes_explored = 1
    
    while frontier:
        # Lấy nút có giá trị heuristic thấp nhất từ hàng đợi
        current = heapq.heappop(frontier)
        
        # Kiểm tra xem trạng thái hiện tại có phải là trạng thái đích không
        if puzzle.is_goal(current.state):
            # Tạo đường đi từ trạng thái đầu đến đích
            path = []
            while current:
                path.append(current.state)
                current = current.parent
            return path[::-1], nodes_explored
        
        # Khám phá tất cả các trạng thái kế tiếp có thể
        for move in puzzle.get_possible_moves(current.state):
            try:
                # Áp dụng bước di chuyển để có trạng thái mới
                new_state = puzzle.apply_move(current.state, move)
                state_string = puzzle.get_state_string(new_state)
                
                # Nếu trạng thái mới chưa được khám phá
                if state_string not in visited:
                    visited.add(state_string)
                    # Tạo nút mới và tính toán giá trị heuristic của nó
                    new_node = Node(new_state, current)
                    new_node.h = manhattan_distance(new_state, puzzle.goal_state)
                    # Thêm vào hàng đợi ưu tiên
                    heapq.heappush(frontier, new_node)
                    nodes_explored += 1
            except ValueError:
                continue  # Bỏ qua các bước đi không hợp lệ
    
    # Không tìm thấy đường đi
    return None, nodes_explored