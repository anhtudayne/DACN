"""
Heuristic functions for 8-puzzle
"""

def manhattan_distance(state, goal_state):
    """
    Tính tổng khoảng cách Manhattan từ mỗi số đến vị trí đích của nó
    """
    distance = 0
    # Tạo dictionary vị trí các số trong goal state
    goal_positions = {}
    for i in range(3):
        for j in range(3):
            goal_positions[goal_state[i][j]] = (i, j)
    
    # Tính tổng khoảng cách Manhattan
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:  # Bỏ qua ô trống
                goal_i, goal_j = goal_positions[state[i][j]]
                distance += abs(i - goal_i) + abs(j - goal_j)
    return distance

def misplaced_tiles(state, goal_state):
    """
    Đếm số ô không đúng vị trí (không tính ô trống)
    """
    count = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0 and state[i][j] != goal_state[i][j]:
                count += 1
    return count 