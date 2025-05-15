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
    """
    Thuật toán Greedy Search (Tìm kiếm tham lam) cho bài toán 8-puzzle.
    
    Nguyên lý hoạt động:
    - Thuật toán Greedy Search lựa chọn nút tiếp theo dựa trên giá trị heuristic thấp nhất.
    - Sử dụng khoảng cách Manhattan từ trạng thái hiện tại đến trạng thái đích làm heuristic.
    - Luôn chọn nút có vẻ "hứa hẹn" nhất tại mỗi bước, không quan tâm đến chi phí đường đi từ đầu đến hiện tại.
    
    Ưu điểm:
    - Tốc độ nhanh, thường tìm ra lời giải trong thời gian ngắn.
    - Tiêu tốn ít bộ nhớ hơn so với BFS vì chỉ mở rộng các nút hứa hẹn.
    - Hiệu quả trong không gian trạng thái lớn với heuristic tốt.
    
    Nhược điểm:
    - Không đảm bảo tìm ra đường đi ngắn nhất.
    - Có thể bị mắc kẹt trong minimum cục bộ nếu heuristic không tốt.
    - Phụ thuộc nhiều vào chất lượng của hàm heuristic được sử dụng.
    
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
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