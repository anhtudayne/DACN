"""Iterative Deepening Search implementation for 8-puzzle"""

def ids_search(puzzle, max_depth=50):
    """
    Thuật toán IDS (Iterative Deepening Search - Tìm kiếm sâu dần) cho bài toán 8-puzzle.
    
    Nguyên lý hoạt động:
    - IDS kết hợp ưu điểm của cả BFS và DFS.
    - Thực hiện một loạt các DFS với độ sâu giới hạn tăng dần.
    - Bắt đầu với độ sâu 0, sau đó tăng dần và chạy DFS với mỗi độ sâu.
    - Đảm bảo tìm ra đường đi ngắn nhất như BFS nhưng tiết kiệm bộ nhớ như DFS.
    
    Ưu điểm:
    - Đảm bảo tìm ra đường đi ngắn nhất, giống như BFS.
    - Tiết kiệm bộ nhớ hơn BFS vì chỉ lưu trữ đường đi hiện tại.
    - Hoạt động tốt với không gian trạng thái lớn.
    
    Nhược điểm:
    - Lặp lại việc khám phá các nút ở độ sâu nông trong mỗi lần lặp.
    - Tổng thời gian thực thi có thể dài hơn BFS.
    
    Tham số:
        puzzle: Đối tượng Puzzle chứa trạng thái đầu và đích
        max_depth: Độ sâu tối đa để tìm kiếm, mặc định là 50
        
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
    if not puzzle.is_solvable():
        return None, 0
    
    # Biến đếm tổng số nút đã khám phá
    total_nodes_explored = 0
    
    # Thực hiện DFS với độ sâu giới hạn tăng dần
    for depth_limit in range(max_depth + 1):
        # Gọi hàm DLS (Depth-Limited Search)
        result, nodes = depth_limited_search(puzzle, depth_limit)
        total_nodes_explored += nodes
        
        # Nếu tìm thấy đường đi, trả về kết quả
        if result is not None:
            return result, total_nodes_explored
    
    # Không tìm thấy đường đi trong giới hạn độ sâu
    return None, total_nodes_explored

def depth_limited_search(puzzle, depth_limit):
    """
    Thuật toán DFS với giới hạn độ sâu (Depth-Limited Search)
    
    Tham số:
        puzzle: Đối tượng Puzzle chứa trạng thái đầu và đích
        depth_limit: Độ sâu tối đa được phép tìm kiếm
        
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
    # Khởi tạo với trạng thái bắt đầu
    stack = [[puzzle.initial_state]]
    visited = {puzzle.get_state_string(puzzle.initial_state)}
    nodes_explored = 1
    
    while stack:
        # Lấy đường đi từ đỉnh ngăn xếp
        path = stack.pop()
        state = path[-1]
        
        # Kiểm tra nếu đã đạt đến trạng thái đích
        if puzzle.is_goal(state):
            return path, nodes_explored
        
        # Nếu chưa đạt đến độ sâu giới hạn, tiếp tục khám phá
        if len(path) <= depth_limit:
            # Khám phá tất cả các trạng thái kế tiếp có thể
            # Lưu ý: Ngược với DFS thông thường, ta duyệt các bước đi theo thứ tự ngược
            # để ưu tiên khám phá theo thứ tự các bước đi tự nhiên
            for move in reversed(puzzle.get_possible_moves(state)):
                try:
                    new_state = puzzle.apply_move(state, move)
                    state_string = puzzle.get_state_string(new_state)
                    
                    # Nếu trạng thái mới chưa được khám phá, thêm vào ngăn xếp
                    if state_string not in visited:
                        visited.add(state_string)
                        new_path = list(path)
                        new_path.append(new_state)
                        stack.append(new_path)
                        nodes_explored += 1
                except ValueError:
                    continue  # Bỏ qua các bước đi không hợp lệ
    
    # Không tìm thấy đường đi với độ sâu giới hạn hiện tại
    return None, nodes_explored
