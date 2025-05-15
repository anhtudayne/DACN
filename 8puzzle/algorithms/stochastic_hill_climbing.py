"""Stochastic Hill Climbing (Leo đồi ngẫu nhiên) implementation for 8-puzzle"""
from .heuristics import manhattan_distance, misplaced_tiles
import random
import math

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state          # Trạng thái hiện tại của puzzle
        self.parent = parent        # Nút cha (trạng thái trước đó)
        self.move = move            # Bước đi dẫn đến trạng thái này
        self.h = 0                  # Giá trị heuristic (khoảng cách Manhattan hoặc số ô sai vị trí)
        
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

def stochastic_hill_climbing(puzzle, heuristic_func=manhattan_distance, max_iterations=1000, probability_threshold=0.3, restart_limit=5):
    """
    Thuật toán Stochastic Hill Climbing (Leo đồi ngẫu nhiên) cho bài toán 8-puzzle.
    
    Định nghĩa:
    - Là một biến thể của thuật toán leo đồi đơn giản.
    - Thay vì tìm ra hàng xóm tốt nhất, phiên bản này lựa chọn ngẫu nhiên một hàng xóm.
    
    Nguyên lý hoạt động:
    - Nếu hàng xóm được chọn tốt hơn trạng thái hiện thời, hàng xóm đó sẽ được chọn làm 
      trạng thái hiện thời và thuật toán lặp lại.
    - Ngược lại, nếu hàng xóm được chọn không tốt hơn, thuật toán sẽ chọn ngẫu nhiên
      một hàng xóm khác và so sánh.
    - Thuật toán kết thúc và trả lại trạng thái hiện thời khi đã hết "kiên nhẫn".
    
    Các bước của thuật toán:
    1. Chọn trạng thái hiện tại
    2. Tạo tất cả các trạng thái lân cận của trạng thái hiện tại
    3. Đánh giá hàm mục tiêu tại tất cả các lân cận
    4. Kiểm tra:
       - Nếu hàm mục tiêu tại trạng thái hiện tại có giá trị cao hơn tất cả lân cận,
         thì trạng thái hiện tại đã là giá trị tối ưu cục bộ, kết thúc tìm kiếm.
       - Nếu không, chọn ngẫu nhiên một lân cận, nếu tốt hơn thì chuyển sang trạng thái đó
    5. Lặp lại bước 2-4 trong n lần lặp hoặc đến khi kiên nhẫn hết
    6. Trả về trạng thái hiện tại và giá trị hàm mục tiêu của nó
    
    Ưu điểm:
    - Khắc phục được điểm yếu về cực trị địa phương của leo đồi đơn giản
    - Thêm yếu tố ngẫu nhiên giúp thuật toán có cơ hội thoát khỏi các cực trị địa phương
    - Đơn giản và nhiều trường hợp hiệu quả hơn các thuật toán leo đồi khác
    
    Nhược điểm:
    - Không đảm bảo tìm ra đường đi tối ưu
    - Có thể mất nhiều thời gian để hội tụ nếu yếu tố ngẫu nhiên khiến thuật toán "lạc đường"
    - Hiệu suất phụ thuộc nhiều vào các tham số xác suất và ngưỡng được chọn
    
    Tham số:
        puzzle: Đối tượng Puzzle chứa trạng thái đầu và đích
        heuristic_func: Hàm hẽuristic được sử dụng để đánh giá trạng thái (mặc định: khoảng cách Manhattan)
        max_iterations: Số lần lặp tối đa ("kiên nhẫn")
        probability_threshold: Ngưỡng xác suất cho việc chấp nhận bước đi xấu hơn
        restart_limit: Số lần khởi động lại ngẫu nhiên
    
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
    # Kiểm tra xem puzzle có thể giải được không
    if not puzzle.is_solvable():
        return None, 0
    
    nodes_explored = 0  # Tổng số nút đã khám phá qua tất cả các lần khởi động lại
    best_solution = None  # Lời giải tốt nhất tìm được
    best_solution_length = float('inf')  # Độ dài của lời giải tốt nhất
    
    # Thử với nhiều lần khởi động lại ngẫu nhiên để thoát khỏi cực tiểu cục bộ
    for restart in range(restart_limit):
        # Nếu đây là lần thử đầu tiên, sử dụng trạng thái ban đầu
        # Nếu không, tạo một trạng thái ngẫu nhiên bằng cách áp dụng các bước di chuyển ngẫu nhiên
        if restart == 0:
            current_state = puzzle.initial_state
        else:
            # Bắt đầu từ trạng thái ban đầu và áp dụng các bước di chuyển ngẫu nhiên
            current_state = puzzle.initial_state
            num_random_moves = random.randint(5, 20)  # Số bước di chuyển ngẫu nhiên
            for _ in range(num_random_moves):
                possible_moves = puzzle.get_possible_moves(current_state)
                if not possible_moves:
                    break
                move = random.choice(possible_moves)
                try:
                    current_state = puzzle.apply_move(current_state, move)
                except ValueError:
                    continue
        
        # Tạo node cho trạng thái hiện tại
        current_node = Node(current_state)
        current_node.h = heuristic_func(current_node.state, puzzle.goal_state)
        
        # Cho lần khởi động này
        restart_nodes_explored = 1  # Số nút đã khám phá trong lần khởi động này
        nodes_explored += 1  # Cập nhật tổng số nút đã khám phá
        visited = {puzzle.get_state_string(current_node.state)}  # Tập các trạng thái đã thăm
        
        # Node tốt nhất cho lần khởi động này
        best_node = current_node
        best_h = current_node.h
        
        iterations = 0  # Số lần lặp cho lần khởi động này
        plateau_count = 0  # Đếm số lần lặp không cải thiện
        
        # Vòng lặp chính của thuật toán
        while not puzzle.is_goal(current_node.state) and iterations < max_iterations:
            # Lấy tất cả các bước di chuyển có thể từ trạng thái hiện tại
            possible_moves = puzzle.get_possible_moves(current_node.state)
            
            # Phân loại các láng giềng
            better_neighbors = []  # Láng giềng tốt hơn (h nhỏ hơn)
            sideways_neighbors = []  # Láng giềng ngang bằng (h bằng nhau)
            uphill_neighbors = []  # Láng giềng xấu hơn (h lớn hơn)
            
            # Đánh giá tất cả các láng giềng có thể
            for move in possible_moves:
                try:
                    # Áp dụng bước di chuyển để có trạng thái mới
                    new_state = puzzle.apply_move(current_node.state, move)
                    new_state_str = puzzle.get_state_string(new_state)
                    
                    # Bỏ qua nếu đã thăm để tránh chu trình
                    if new_state_str in visited:
                        continue
                        
                    # Tạo node mới và tính giá trị heuristic
                    new_node = Node(new_state, current_node, move)
                    new_node.h = heuristic_func(new_state, puzzle.goal_state)
                    restart_nodes_explored += 1
                    nodes_explored += 1
                    
                    # Xác định xem láng giềng này tốt hơn, ngang bằng hay xấu hơn
                    if new_node.h < current_node.h:
                        # Lưu trữ mức độ cải thiện (delta h)
                        improvement = current_node.h - new_node.h
                        better_neighbors.append((new_node, improvement))
                    elif new_node.h == current_node.h:
                        sideways_neighbors.append(new_node)
                    else:
                        # Đối với các bước đi đi lên đồi, tính mức độ xấu hơn
                        worsening = new_node.h - current_node.h
                        uphill_neighbors.append((new_node, worsening))
                    
                    # Cập nhật node tốt nhất nếu tìm thấy trạng thái tốt hơn
                    if new_node.h < best_h:
                        best_node = new_node
                        best_h = new_node.h
                        plateau_count = 0  # Đặt lại bộ đếm bình nguyên
                    
                except ValueError:
                    continue  # Bỏ qua các bước di chuyển không hợp lệ
            
            iterations += 1
            
            # Chiến lược ra quyết định
            if better_neighbors:
                # Chọn ngẫu nhiên từ các láng giềng tốt hơn
                # Mức cải thiện càng cao, xác suất được chọn càng lớn
                total_improvement = sum(imp for _, imp in better_neighbors)
                probabilities = [imp / total_improvement for _, imp in better_neighbors]
                
                # Chọn một node dựa trên xác suất
                selected_index = random.choices(range(len(better_neighbors)), weights=probabilities, k=1)[0]
                selected_node = better_neighbors[selected_index][0]
                
                # Di chuyển đến node đã chọn
                current_node = selected_node
                visited.add(puzzle.get_state_string(current_node.state))
                
            elif sideways_neighbors and plateau_count < 5:
                # Cho phép một số di chuyển ngang để thoát khỏi bình nguyên
                selected_node = random.choice(sideways_neighbors)
                current_node = selected_node
                visited.add(puzzle.get_state_string(current_node.state))
                plateau_count += 1
                
            elif uphill_neighbors and random.random() < probability_threshold:
                # Thỉnh thoảng chấp nhận các bước đi đi lên đồi, ưu tiên các bước đi lên ít hơn
                # Sắp xếp theo mức độ xấu đi (tăng dần)
                uphill_neighbors.sort(key=lambda x: x[1])
                
                # Nhiều cơ hội để chọn các bước đi lên đồi nhỏ hơn
                uphill_weights = [math.exp(-w/2) for _, w in uphill_neighbors]
                total_weight = sum(uphill_weights)
                uphill_probs = [w/total_weight for w in uphill_weights]
                
                selected_index = random.choices(range(len(uphill_neighbors)), weights=uphill_probs, k=1)[0]
                selected_node = uphill_neighbors[selected_index][0]
                
                current_node = selected_node
                visited.add(puzzle.get_state_string(current_node.state))
                plateau_count = 0  # Đặt lại bình nguyên khi di chuyển
                
            else:
                # Nếu không có láng giềng để khám phá hoặc bị kẹt trên bình nguyên, sử dụng node tốt nhất đã thấy
                if best_h < current_node.h:
                    current_node = best_node
                    plateau_count = 0  # Đặt lại bộ đếm bình nguyên
                else:
                    # Chúng ta thực sự bị kẹt, kết thúc lần thử này
                    break
        
        # Nếu tìm thấy đích, tái tạo đường đi
        if puzzle.is_goal(current_node.state):
            path = []
            node = current_node
            while node:
                path.append(node.state)
                node = node.parent
            path.reverse()
            
            # Nếu đây là lời giải tốt nhất cho đến nay, ghi nhớ nó
            if len(path) < best_solution_length:
                best_solution = path
                best_solution_length = len(path)
                
            # Nếu chúng ta đã tìm thấy một lời giải tốt, có thể dừng lại
            if best_solution_length <= 20:  # Ngưỡng tùy ý cho một lời giải "đủ tốt"
                break
    
    # Trả về lời giải tốt nhất tìm thấy qua tất cả các lần thử
    return best_solution, nodes_explored
