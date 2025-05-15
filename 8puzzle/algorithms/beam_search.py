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
    """
    Thuật toán Tìm kiếm Chùm tia (Beam Search) cho bài toán 8-puzzle.
    
    Định nghĩa:
    - Beam Search là một thuật toán tìm kiếm có giới hạn bộ nhớ (memory-bounded), mở rộng các trạng thái tốt nhất theo chiều rộng.
    - Thuật toán duy trì một tập các trạng thái đang xét gọi là "beam" (chùm tia) có kích thước cố định.
    
    Nguyên lý hoạt động:
    - Là sự kết hợp giữa tìm kiếm theo chiều rộng (BFS) và tìm kiếm tốt nhất đầu tiên (Best-First Search).
    - Tại mỗi mức của cây tìm kiếm, thuật toán chỉ giữ lại k trạng thái tốt nhất, với k là độ rộng chùm tia (beam width).
    - Sử dụng hàm heuristic để đánh giá và lựa chọn các trạng thái tốt nhất để mở rộng.
    
    Các bước thực hiện:
    1. Khởi tạo beam với trạng thái ban đầu.
    2. Lặp lại cho đến khi tìm thấy trạng thái đích hoặc beam trống:
       a. Tạo tất cả các trạng thái kế tiếp có thể từ các trạng thái trong beam hiện tại.
       b. Đánh giá tất cả các trạng thái kế tiếp bằng hàm heuristic.
       c. Chọn k trạng thái tốt nhất để tạo thành beam mới.
    3. Trả về đường đi từ trạng thái ban đầu đến trạng thái đích (nếu tìm thấy).
    
    Ưu điểm:
    - Tối ưu hóa về bộ nhớ: Chỉ lưu trữ một số lượng cố định trạng thái (beam_width) tại mỗi mức độ.
    - Nhanh hơn so với tìm kiếm theo chiều rộng đầy đủ do giới hạn số trạng thái được mở rộng.
    - Dễ dàng điều chỉnh giữa hiệu suất và chất lượng lời giải bằng cách thay đổi beam_width.
    - Không bị kẹt trong các vòng lặp vô hạn như tìm kiếm theo chiều sâu.
    
    Nhược điểm:
    - Không đảm bảo tìm được lời giải tối ưu, do có thể bỏ sót các đường đi tiềm năng dẫn đến lời giải.
    - Không đầy đủ: Có thể bỏ qua các đường đi dẫn đến lời giải nếu beam quá hẹp.
    - Phụ thuộc nhiều vào hàm heuristic: Nếu hàm heuristic không tốt, thuật toán có thể loại bỏ các trạng thái quan trọng.
    - Khó xác định độ rộng chùm tia tối ưu: Beam quá nhỏ có thể bỏ qua lời giải, beam quá lớn có thể làm giảm hiệu suất.
    
    Tham số:
        puzzle: Đối tượng Puzzle chứa trạng thái đầu và đích
        beam_width: Độ rộng chùm tia (số trạng thái giữ lại tại mỗi mức độ)
        heuristic_func: Hàm đánh giá trạng thái, mặc định sử dụng khoảng cách Manhattan
    
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
    if not puzzle.is_solvable():
        return None, 0
        
    # Create initial node
    initial_node = Node(puzzle.initial_state)
    initial_node.h = heuristic_func(initial_node.state, puzzle.goal_state)
    initial_node.f = initial_node.g + initial_node.h
    
    # Check if initial state is goal
    if puzzle.is_goal(initial_node.state):
        return [initial_node.state], 1
    
    # Initialize beam with initial node
    beam = [initial_node]
    
    # Track visited states
    visited = {puzzle.get_state_string(initial_node.state)}
    
    # Counter for nodes explored
    nodes_explored = 1
    
    while beam:
        # Get all successors of current beam
        all_successors = []
        
        for node in beam:
            possible_moves = puzzle.get_possible_moves(node.state)
            
            for move in possible_moves:
                try:
                    new_state = puzzle.apply_move(node.state, move)
                    state_str = puzzle.get_state_string(new_state)
                    
                    # Skip if already visited
                    if state_str in visited:
                        continue
                    
                    # Create new node
                    new_node = Node(new_state, node, move, node.g + 1)
                    new_node.h = heuristic_func(new_state, puzzle.goal_state)
                    new_node.f = new_node.g + new_node.h
                    
                    # Check if goal
                    if puzzle.is_goal(new_state):
                        # Reconstruct path
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
        
        # If no successors, algorithm fails
        if not all_successors:
            return None, nodes_explored
        
        # Select best beam_width nodes
        beam = heapq.nsmallest(beam_width, all_successors)
    
    # If beam is empty and goal not found, algorithm fails
    return None, nodes_explored
