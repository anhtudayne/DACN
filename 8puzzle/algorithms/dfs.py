"""Depth-First Search implementation for 8-puzzle"""

def dfs_search(puzzle, max_depth=200):
    """
    Thuật toán DFS (Depth-First Search - Tìm kiếm theo chiều sâu) cho bài toán 8-puzzle.
    
    Nguyên lý hoạt động:
    - DFS sẽ khám phá càng sâu càng tốt theo từng nhánh trước khi quay lại khám phá các nhánh khác.
    - Sử dụng cấu trúc dữ liệu ngăn xếp (stack) với nguyên tắc LIFO (Last In First Out).
    - Thuật toán sẽ ưu tiên khám phá theo chiều sâu của cây trạng thái.
    
    Ưu điểm:
    - Tiết kiệm bộ nhớ hơn BFS trong nhiều trường hợp.
    - Có thể tìm ra đường đi nhanh hơn BFS trong một số trường hợp đặc biệt.
    
    Nhược điểm:
    - Có thể rơi vào đường đi rất dài hoặc vòng lặp vô hạn.
    - Không đảm bảo tìm ra đường đi ngắn nhất.
    - Với 8-puzzle, DFS thường kém hiệu quả hơn BFS vì không gian trạng thái rộng.
    
    Tham số:
        puzzle: Đối tượng Puzzle chứa trạng thái đầu và đích
        max_depth: Độ sâu tối đa để tránh bị rơi vào vòng lặp quá sâu
        
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
    if not puzzle.is_solvable():
        return None, 0
        
    # Khởi tạo với trạng thái bắt đầu
    stack = [[puzzle.initial_state]]
    visited = {puzzle.get_state_string(puzzle.initial_state)}
    nodes_explored = 1
    
    while stack:
        # Lấy đường đi trên cùng của ngăn xếp (khác với BFS lấy từ đầu hàng đợi)
        path = stack.pop()
        state = path[-1]
        
        # Kiểm tra nếu đã đạt đến trạng thái đích
        if puzzle.is_goal(state):
            return path, nodes_explored
            
        # Nếu đã đạt đến độ sâu tối đa, bỏ qua trạng thái này
        if len(path) > max_depth:
            continue
            
        # Khám phá tất cả các trạng thái kế tiếp có thể có
        for move in puzzle.get_possible_moves(state):
            try:
                new_state = puzzle.apply_move(state, move)
                state_string = puzzle.get_state_string(new_state)
                
                # Nếu trạng thái mới chưa được khám phá, thêm vào ngăn xếp
                if state_string not in visited:
                    visited.add(state_string)
                    new_path = list(path)
                    new_path.append(new_state)
                    # Đẩy vào ngăn xếp (khác với BFS thêm vào cuối hàng đợi)
                    stack.append(new_path)
                    nodes_explored += 1
            except ValueError:
                continue  # Bỏ qua các bước đi không hợp lệ
    
    # Không tìm thấy đường đi
    return None, nodes_explored
