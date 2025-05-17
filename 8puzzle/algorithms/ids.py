"""Iterative Deepening Search implementation for 8-puzzle"""

def ids_search(puzzle, max_depth=50):
   
    if not puzzle.is_solvable():
        return None, 0
    
    total_nodes_explored = 0
    
    for depth_limit in range(max_depth + 1):
        result, nodes = depth_limited_search(puzzle, depth_limit)
        total_nodes_explored += nodes
        
        # Nếu tìm thấy đường đi, trả về kết quả
        if result is not None:
            return result, total_nodes_explored
    
    # Không tìm thấy đường đi trong giới hạn độ sâu
    return None, total_nodes_explored

def depth_limited_search(puzzle, depth_limit):
   
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
