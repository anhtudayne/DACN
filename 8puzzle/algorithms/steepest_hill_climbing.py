"""Steepest-Ascent Hill Climbing (Leo đồi dốc nhất) implementation for 8-puzzle"""
from .heuristics import manhattan_distance, misplaced_tiles

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state          # Trạng thái hiện tại của puzzle
        self.parent = parent        # Nút cha (trạng thái trước)
        self.move = move            # Bước đi dẫn đến trạng thái này
        self.h = 0                  # Giá trị heuristic (khoảng cách Manhattan hoặc số ô sai vị trí)
        
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

def steepest_hill_climbing(puzzle, heuristic_func=manhattan_distance):
    """
    Thuật toán Steepest-Ascent Hill Climbing (Leo đồi dốc nhất) cho bài toán 8-puzzle.
    
    Định nghĩa:
    - Là một biến thể của thuật toán leo đồi đơn giản.
    - Thuật toán này kiểm tra tất cả các nút lân cận của trạng thái hiện tại
      và chọn một nút lân cận gần nhất với trạng thái mục tiêu.
    
    Nguyên lý hoạt động:
    - Khác với leo đồi đơn giản, leo đồi dốc nhất đánh giá TẤT CẢ các trạng thái lân cận
      trước khi chọn trạng thái tốt nhất để di chuyển.
    - Thuật toán lựa chọn trạng thái lân cận có giá trị hàm mục tiêu tốt nhất.
    
    Các bước của thuật toán:
    1. Chọn trạng thái hiện tại
    2. Tạo tất cả các trạng thái lân cận của trạng thái hiện tại
    3. Đánh giá hàm mục tiêu tại tất cả các trạng thái lân cận
    4. Kiểm tra:
       - Nếu hàm mục tiêu tại trạng thái hiện tại có giá trị cao hơn tất cả các trạng thái lân cận,
         thì trạng thái hiện tại đã là giá trị tối ưu cục bộ, kết thúc tìm kiếm.
       - Nếu không, lân cận có giá trị tốt nhất sẽ trở thành trạng thái hiện tại mới
    5. Lặp lại bước 2-4 trong n lần lặp
    6. Trả về trạng thái hiện tại và giá trị hàm mục tiêu của nó
    
    Ưu điểm:
    - Tìm ra giải pháp tốt hơn so với leo đồi đơn giản vì xem xét tất cả các lân cận
    - Ít bị mắc kẹt ở cực trị địa phương hơn so với leo đồi đơn giản
    - Tiết kiệm bộ nhớ hơn so với các thuật toán tìm kiếm dựa trên đồ thị
    
    Nhược điểm:
    - Vẫn có thể bị mắc kẹt ở cực trị địa phương
    - Không đảm bảo tìm ra đường đi tối ưu (ngắn nhất)
    - Thời gian xử lý lâu hơn so với leo đồi đơn giản vì đánh giá tất cả các trạng thái lân cận
    
    Tham số:
        puzzle: Đối tượng Puzzle chứa trạng thái đầu và đích
        heuristic_func: Hàm hẽuristic được sử dụng để đánh giá trạng thái (mặc định: khoảng cách Manhattan)
    
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
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
        # Bước 2: Tạo tất cả các trạng thái lân cận (hàng xóm)
        possible_moves = puzzle.get_possible_moves(current_node.state)
        
        # Khởi tạo nút tốt nhất và giá trị heuristic tốt nhất 
        best_node = None
        best_h = current_node.h
        
        # Bước 3: Đánh giá tất cả các trạng thái lân cận để tìm trạng thái tốt nhất
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
                
                # Nếu trạng thái này tốt hơn trạng thái tốt nhất hiện tại, cập nhật
                if new_node.h < best_h:
                    best_node = new_node
                    best_h = new_node.h
                    
            except ValueError:
                continue  # Bỏ qua các bước đi không hợp lệ
        
        # Bước 4: Kiểm tra điều kiện dừng hoặc tiếp tục
        # Nếu không tìm thấy trạng thái nào tốt hơn, chúng ta đã bị mắc kẹt ở cực trị địa phương
        if best_node is None:
            return None, nodes_explored
            
        # Nếu tìm thấy trạng thái tốt hơn, di chuyển đến trạng thái đó
        current_node = best_node
        visited.add(puzzle.get_state_string(current_node.state))
        path_nodes[puzzle.get_state_string(current_node.state)] = current_node
    
    # Bước 6: Tìm thấy trạng thái đích, tái tạo đường đi
    path = []
    while current_node:
        path.append(current_node.state)
        current_node = current_node.parent
    
    # Đảo ngược đường đi để có thứ tự từ trạng thái đầu đến đích
    return path[::-1], nodes_explored
