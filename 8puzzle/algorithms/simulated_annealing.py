"""Thuật toán Mô phỏng Luyện kim (Simulated Annealing) cho bài toán 8-puzzle"""
from .heuristics import manhattan_distance, misplaced_tiles
import random
import math

class Node:
    """
    Lớp Node đại diện cho một trạng thái của puzzle
    """
    def __init__(self, state, parent=None, move=None):
        self.state = state  # Trạng thái hiện tại của puzzle
        self.parent = parent  # Node cha (trạng thái trước đó)
        self.move = move  # Bước di chuyển từ trạng thái cha đến trạng thái hiện tại
        self.h = 0  # Giá trị hàm heuristic (khoảng cách Manhattan hoặc số ô sai vị trí)
        
    def __eq__(self, other):
        # Hai node được coi là bằng nhau nếu có cùng trạng thái
        return isinstance(other, Node) and self.state == other.state

def simulated_annealing(puzzle, heuristic_func=manhattan_distance, initial_temp=1000, cooling_rate=0.97, min_temp=0.01, max_iterations=10000):
   
    # Kiểm tra xem puzzle có thể giải được không
    if not puzzle.is_solvable():
        return None, 0
    
    # Tạo nút ban đầu
    current_node = Node(puzzle.initial_state)
    current_node.h = heuristic_func(current_node.state, puzzle.goal_state)
    
    # Node tốt nhất đã thấy cho đến hiện tại
    best_node = current_node
    best_h = current_node.h
    
    # Từ điển lưu trữ các node để tái tạo đường đi
    nodes_dict = {puzzle.get_state_string(current_node.state): current_node}
    
    # Khởi tạo nhiệt độ và số lượng nút đã khám phá
    temp = initial_temp
    nodes_explored = 1
    iterations = 0
    
    # Theo dõi các trạng thái đã thăm để tránh lặp
    visited = set([puzzle.get_state_string(current_node.state)])
    
    # Vòng lặp chính của thuật toán
    while temp > min_temp and iterations < max_iterations:
        # Kiểm tra xem đã đạt đến trạng thái đích chưa
        if puzzle.is_goal(current_node.state):
            # Tái tạo đường đi
            path = []
            while current_node:
                path.append(current_node.state)
                current_node = current_node.parent
            
            # Đảo ngược đường đi để có thứ tự đúng: từ trạng thái ban đầu đến đích
            return path[::-1], nodes_explored
        
        # Lấy tất cả các bước đi có thể từ trạng thái hiện tại
        possible_moves = puzzle.get_possible_moves(current_node.state)
        
        # Nếu bị kẹt (không có bước đi hợp lệ), thử quay lại trạng thái tốt nhất
        if not possible_moves:
            if best_h < current_node.h:
                current_node = best_node
            continue
        
        # Thử từng bước đi có thể thay vì chỉ chọn một bước ngẫu nhiên
        found_better_state = False  # Đánh dấu nếu tìm thấy trạng thái tốt hơn
        valid_neighbors = []  # Danh sách các trạng thái kề hợp lệ
        
        for move in possible_moves:
            try:
                # Áp dụng bước đi để có trạng thái mới
                new_state = puzzle.apply_move(current_node.state, move)
                state_str = puzzle.get_state_string(new_state)
                
                # Bỏ qua nếu đã thăm (tránh chu trình)
                if state_str in visited:
                    continue
                    
                # Tạo node mới và tính giá trị heuristic
                new_node = Node(new_state, current_node, move)
                new_node.h = heuristic_func(new_state, puzzle.goal_state)
                nodes_explored += 1
                
                # Thêm vào danh sách láng giềng hợp lệ
                valid_neighbors.append((new_node, new_node.h))
                
                # Nếu tìm thấy đích, trả về ngay lập tức
                if puzzle.is_goal(new_state):
                    path = []
                    current_node = new_node
                    while current_node:
                        path.append(current_node.state)
                        current_node = current_node.parent
                    return path[::-1], nodes_explored
                
                # Cập nhật node tốt nhất nếu tìm thấy trạng thái tốt hơn
                if new_node.h < best_h:
                    best_node = new_node
                    best_h = new_node.h
                    found_better_state = True
                
            except ValueError:
                continue  # Bỏ qua các bước đi không hợp lệ
        
        # Nếu tìm thấy láng giềng hợp lệ, chọn một dựa trên xác suất của Simulated Annealing
        if valid_neighbors:
            # Sắp xếp theo giá trị heuristic (tăng dần)
            valid_neighbors.sort(key=lambda x: x[1])
            
            # Chọn láng giềng ngẫu nhiên, ưu tiên các láng giềng tốt hơn khi nhiệt độ thấp
            if random.random() < 0.1:  # 10% cơ hội chọn hoàn toàn ngẫu nhiên
                selected_node = random.choice(valid_neighbors)[0]
            else:
                # Tính xác suất lựa chọn dựa trên heuristic và nhiệt độ
                total_h = sum(1.0 / (n[1] + 1) for n in valid_neighbors)  # Cộng 1 để tránh chia cho 0
                probabilities = [(1.0 / (n[1] + 1)) / total_h for n in valid_neighbors]
                
                # Chọn node dựa trên xác suất
                indexes = list(range(len(valid_neighbors)))
                selected_index = random.choices(indexes, weights=probabilities, k=1)[0]
                selected_node, selected_h = valid_neighbors[selected_index]
                
                # Tính delta E (thay đổi năng lượng/heuristic)
                delta_h = selected_h - current_node.h
                
                # Nếu trạng thái mới tốt hơn (h thấp hơn), chấp nhận nó
                # Nếu không, chấp nhận với xác suất dựa trên nhiệt độ
                if delta_h <= 0 or random.random() < math.exp(-delta_h / temp):
                    visited.add(puzzle.get_state_string(selected_node.state))
                    current_node = selected_node
        
        # Nếu bị kẹt, khởi động lại từ node tốt nhất đã thấy
        elif best_h < current_node.h:
            current_node = best_node
        
        # Làm mát nhiệt độ theo lịch trình phức tạp hơn
        # Làm mát chậm lúc đầu, nhanh hơn về sau
        if iterations < max_iterations / 3:
            temp *= cooling_rate  # Làm mát chậm lúc đầu
        else:
            temp *= (cooling_rate ** 2)  # Làm mát nhanh hơn về sau
            
        iterations += 1
        
        # Định kỳ kiểm tra xem có thể làm nóng lại để thoát khỏi cực tiểu cục bộ
        if iterations % 100 == 0 and not found_better_state:
            temp = min(temp * 1.5, initial_temp / 2)  # Làm nóng lại nhưng không đến nhiệt độ ban đầu
    
    # Nếu không tìm thấy đích nhưng có trạng thái tốt nhất
    # Thử tái tạo đường đi đến trạng thái tốt nhất
    if best_node and best_h < current_node.h:
        current_node = best_node
    
    # Nếu đang ở trạng thái đích, trả về đường đi
    if puzzle.is_goal(current_node.state):
        path = []
        while current_node:
            path.append(current_node.state)
            current_node = current_node.parent
        return path[::-1], nodes_explored
    
    # Không tìm thấy lời giải
    return None, nodes_explored
