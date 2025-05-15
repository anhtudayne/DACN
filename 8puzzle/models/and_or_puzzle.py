"""
Class Puzzle đặc biệt cho thuật toán AND-OR search
"""
import copy
import random

class AndOrPuzzle:
    """Lớp đại diện cho bài toán 8-puzzle đơn giản cho thuật toán AND-OR Search"""
    
    def __init__(self, initial_state=None, goal_state=None):
        """
        Khởi tạo đối tượng AndOrPuzzle.
        
        Tham số:
        - initial_state: Trạng thái bắt đầu
        - goal_state: Trạng thái mục tiêu
        """
        # Trạng thái mục tiêu mặc định (đã giải)
        self.goal_state = goal_state or [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        
        # Trạng thái ban đầu (ở đây là trạng thái đơn giản chỉ cần 1 bước)
        self.initial_state = initial_state or [
            [1, 2, 3],
            [4, 5, 6],
            [7, 0, 8]
        ]
    
    def is_valid_state(self, state):
        """Kiểm tra xem trạng thái có hợp lệ không (chứa đúng các số từ 0-8)."""
        # Kiểm tra kích thước
        if len(state) != 3 or any(len(row) != 3 for row in state):
            return False
        
        # Kiểm tra nội dung
        flat_state = [item for sublist in state for item in sublist]
        return sorted(flat_state) == list(range(9))
    
    def is_goal(self, state):
        """Kiểm tra xem trạng thái có phải là trạng thái mục tiêu không."""
        # So sánh từng phần tử
        for i in range(len(state)):
            for j in range(len(state[i])):
                if state[i][j] != self.goal_state[i][j]:
                    return False
        return True
    
    def get_blank_position(self, state):
        """Tìm vị trí của ô trống (0) trong trạng thái."""
        for i in range(len(state)):
            for j in range(len(state[i])):
                if state[i][j] == 0:
                    return (i, j)
        raise ValueError("Không tìm thấy ô trống trong trạng thái")
    
    def get_possible_moves(self, state):
        """Trả về danh sách các hành động hợp lệ từ trạng thái hiện tại."""
        moves = []
        i, j = self.get_blank_position(state)
        
        # Kiểm tra và thêm các hành động hợp lệ
        if i > 0:  # Có thể di chuyển lên
            moves.append('up')
        if i < 2:  # Có thể di chuyển xuống
            moves.append('down')
        if j > 0:  # Có thể di chuyển sang trái
            moves.append('left')
        if j < 2:  # Có thể di chuyển sang phải
            moves.append('right')
        
        return moves
    
    def apply_move(self, state, move):
        """Áp dụng hành động lên trạng thái và trả về trạng thái mới."""
        # Tạo bản sao để không thay đổi trạng thái gốc
        new_state = [row[:] for row in state]
        
        # Lấy vị trí ô trống
        i, j = self.get_blank_position(state)
        
        # Di chuyển ô trống theo hành động
        if move == 'up' and i > 0:  # Di chuyển lên
            new_state[i][j], new_state[i-1][j] = new_state[i-1][j], new_state[i][j]
        elif move == 'down' and i < 2:  # Di chuyển xuống
            new_state[i][j], new_state[i+1][j] = new_state[i+1][j], new_state[i][j]
        elif move == 'left' and j > 0:  # Di chuyển sang trái
            new_state[i][j], new_state[i][j-1] = new_state[i][j-1], new_state[i][j]
        elif move == 'right' and j < 2:  # Di chuyển sang phải
            new_state[i][j], new_state[i][j+1] = new_state[i][j+1], new_state[i][j]
        else:
            raise ValueError(f"Hành động {move} không hợp lệ từ vị trí ({i},{j})")
        
        return new_state
