"""Simple Hill Climbing (Leo đồi đơn giản) implementation for 8-puzzle"""
from .heuristics import manhattan_distance, misplaced_tiles

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state          # Trạng thái hiện tại của puzzle
        self.parent = parent        # Nút cha (trạng thái trước)
        self.move = move            # Bước đi dẫn đến trạng thái này
        self.h = 0                  # Giá trị heuristic (khoảng cách Manhattan hoặc số ô sai vị trí)
        
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

def simple_hill_climbing(puzzle, heuristic_func=manhattan_distance):
   
    # Kiểm tra tính giải được của puzzle
    if not puzzle.is_solvable():
        return None, 0
    
    # Bước 1: Khởi tạo trạng thái hiện tại
    current_node = Node(puzzle.initial_state)
    current_node.h = heuristic_func(current_node.state, puzzle.goal_state)
    
    # Đếm số nút đã khám phá
    nodes_explored = 1
    # Tập hợp các trạng thái đã thăm
    visited = {puzzle.get_state_string(current_node.state)}
    
    # Lưu trữ các nút để tái tạo đường đi
    path_nodes = {puzzle.get_state_string(current_node.state): current_node}
    
    # Vòng lặp chính - lặp đi lặp lại cho đến khi tìm thấy trạng thái đích hoặc không có trạng thái nào tốt hơn
    while not puzzle.is_goal(current_node.state):
        # Bước 2: Tạo các trạng thái hàng xóm (lân cận)
        possible_moves = puzzle.get_possible_moves(current_node.state)
        found_better = False
        
        # Bước 3 và 4: Đánh giá hàm mục tiêu và tìm trạng thái tốt hơn
        for move in possible_moves:
            try:
                # Tạo trạng thái mới từ bước đi hiện tại
                new_state = puzzle.apply_move(current_node.state, move)
                new_state_str = puzzle.get_state_string(new_state)
                
                # Bỏ qua nếu trạng thái đã thăm
                if new_state_str in visited:
                    continue
                
                # Tạo nút mới và tính toán giá trị heuristic của nó
                new_node = Node(new_state, current_node, move)
                new_node.h = heuristic_func(new_state, puzzle.goal_state)
                nodes_explored += 1
                
                # So sánh giá trị: nếu trạng thái mới tốt hơn, di chuyển đến đó
                if new_node.h < current_node.h:
                    current_node = new_node
                    visited.add(new_state_str)
                    path_nodes[new_state_str] = new_node
                    found_better = True
                    break  # Lấy trạng thái đầu tiên tốt hơn và tiếp tục
                    
            except ValueError:
                continue  # Bỏ qua các bước đi không hợp lệ
        
        # Bước 5: Kiểm tra điều kiện dừng
        # Nếu không tìm thấy trạng thái nào tốt hơn, chúng ta đã bị mắc kẹt ở cực trị địa phương
        if not found_better:
            return None, nodes_explored
    
    # Bước 6: Tìm thấy trạng thái đích, tái tạo đường đi
    path = []
    while current_node:
        path.append(current_node.state)
        current_node = current_node.parent
    
    # Đảo ngược đường đi để có thứ tự từ trạng thái đầu đến đích
    return path[::-1], nodes_explored
