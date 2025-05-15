import copy

class SensorlessPuzzle:
    """
    Lớp mô tả bài toán 8-puzzle trong môi trường không quan sát.
    Thay vì một trạng thái duy nhất, chúng ta làm việc với belief states - 
    tập hợp các trạng thái mà puzzle có thể đang ở.
    """
    
    def __init__(self):
        """
        Khởi tạo puzzle với initial belief state và goal states cố định.
        """
        # Initial belief state - 2 cấu hình đại diện cố định
        self.initial_belief_state = [
            # Cấu hình 1 - trạng thái gần với goal
            [[1, 2, 3], [4, 5, 6], [7, 0, 8]],
            # Cấu hình 2 - trạng thái với ô trống ở góc
            [[1, 2, 3], [4, 5, 0], [7, 8, 6]]
        ]
        
        # Goal states - 5 cấu hình đại diện cố định
        self.goal_states = [
            # Goal chuẩn
            [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            # Biến thể 1: đổi vị trí 7 và 8
            [[1, 2, 3], [4, 5, 6], [8, 7, 0]],
            # Biến thể 2: đổi vị trí 5 và 6
            [[1, 2, 3], [4, 6, 5], [7, 8, 0]],
            # Biến thể 3: đổi vị trí 2 và 3
            [[1, 3, 2], [4, 5, 6], [7, 8, 0]],
            # Biến thể 4: đổi vị trí 4 và 7
            [[1, 2, 3], [7, 5, 6], [4, 8, 0]]
        ]
    
    def get_initial_belief_state(self):
        """Trả về belief state ban đầu."""
        return self.initial_belief_state
    
    def get_goal_states(self):
        """Trả về các trạng thái đích."""
        return self.goal_states
    
    def get_actions(self, belief_state):
        """
        Trả về tập hợp các hành động hợp lệ trên belief state.
        Đây là union của tất cả các hành động hợp lệ trên các trạng thái trong belief state.
        """
        all_actions = set()
        
        # Kiểm tra trước khi truy cập belief state
        if not belief_state or not isinstance(belief_state, list):
            print(f"Lỗi: Belief state không hợp lệ: {belief_state}")
            return []
        
        for state in belief_state:
            # Tìm vị trí ô trống
            empty_row, empty_col = self._find_empty(state)
            
            # Kiểm tra xem có tìm thấy ô trống không
            if empty_row == -1 or empty_col == -1:
                # Bỏ qua trạng thái này nếu không tìm thấy ô trống
                continue
                
            # Xác định các hành động hợp lệ
            if empty_row > 0:
                all_actions.add("UP")
            if empty_row < 2:
                all_actions.add("DOWN")
            if empty_col > 0:
                all_actions.add("LEFT")
            if empty_col < 2:
                all_actions.add("RIGHT")
        
        return list(all_actions)
    
    def apply_action(self, belief_state, action):
        """
        Áp dụng một hành động lên tất cả các trạng thái trong belief state.
        Trả về belief state mới sau khi áp dụng hành động.
        """
        new_belief_state = []
        
        # Kiểm tra trước khi truy cập belief state
        if not belief_state or not isinstance(belief_state, list):
            print(f"Lỗi: Belief state không hợp lệ trong apply_action: {belief_state}")
            return []
            
        for state in belief_state:
            # Tìm vị trí ô trống
            empty_row, empty_col = self._find_empty(state)
            
            # Kiểm tra trước khi xử lý trạng thái
            if empty_row == -1 or empty_col == -1:
                # Bỏ qua trạng thái này nếu không tìm thấy ô trống
                continue
            
            # Áp dụng hành động nếu hợp lệ
            new_state = self._deep_copy(state)
            applied = False
            
            if action == "UP" and empty_row > 0:
                # Di chuyển ô trống lên
                new_state[empty_row][empty_col] = new_state[empty_row-1][empty_col]
                new_state[empty_row-1][empty_col] = 0
                applied = True
            elif action == "DOWN" and empty_row < 2:
                # Di chuyển ô trống xuống
                new_state[empty_row][empty_col] = new_state[empty_row+1][empty_col]
                new_state[empty_row+1][empty_col] = 0
                applied = True
            elif action == "LEFT" and empty_col > 0:
                # Di chuyển ô trống sang trái
                new_state[empty_row][empty_col] = new_state[empty_row][empty_col-1]
                new_state[empty_row][empty_col-1] = 0
                applied = True
            elif action == "RIGHT" and empty_col < 2:
                # Di chuyển ô trống sang phải
                new_state[empty_row][empty_col] = new_state[empty_row][empty_col+1]
                new_state[empty_row][empty_col+1] = 0
                applied = True
            
            # Thêm trạng thái mới vào belief state mới nếu chưa có
            if applied and not self._state_in_list(new_state, new_belief_state):
                new_belief_state.append(new_state)
            elif not applied and not self._state_in_list(state, new_belief_state):
                # Nếu không thể áp dụng hành động, giữ nguyên trạng thái
                new_belief_state.append(state)
        
        # Kiểm tra nếu belief state mới rỗng, trả về belief state gốc để tránh lỗi
        if not new_belief_state:
            print(f"Cảnh báo: Belief state mới rỗng sau khi áp dụng hành động {action}")
            return belief_state
            
        return new_belief_state
    
    def is_goal(self, belief_state):
        """
        Kiểm tra xem belief state có đạt mục tiêu không.
        Một belief state đạt mục tiêu khi TẤT CẢ các trạng thái trong belief state
        đều là các goal states (theo định nghĩa của Sensorless Search).
        """
        # Kiểm tra trước khi truy cập belief state
        if not belief_state or not isinstance(belief_state, list):
            print(f"Lỗi: Belief state không hợp lệ trong is_goal: {belief_state}")
            return False
            
        # Nếu belief state rỗng, không đạt goal
        if len(belief_state) == 0:
            return False
            
        # Kiểm tra từng trạng thái trong belief state
        for state in belief_state:
            # Kiểm tra nếu trạng thái không hợp lệ
            if not state or not isinstance(state, list) or len(state) != 3:
                print(f"Lỗi: Trạng thái không hợp lệ trong is_goal: {state}")
                continue
                
            is_goal_state = False
            
            # Kiểm tra xem trạng thái này có phải là một trong các goal states không
            for goal_state in self.goal_states:
                if self._is_same_state(state, goal_state):
                    is_goal_state = True
                    break
                    
            # Nếu có một trạng thái không phải goal state, trả về False
            if not is_goal_state:
                return False
        
        # Tất cả các trạng thái đều là goal states
        return True
    
    def _find_empty(self, state):
        """Tìm vị trí ô trống (giá trị 0) trong trạng thái."""
        # Kiểm tra trước khi truy cập để tránh lỗi index out of range
        if not state or not isinstance(state, list) or len(state) != 3:
            print(f"Lỗi: Trạng thái không hợp lệ: {state}")
            return -1, -1
            
        for i in range(3):
            if not isinstance(state[i], list) or len(state[i]) != 3:
                print(f"Lỗi: Hàng {i} không hợp lệ: {state[i]}")
                return -1, -1
                
            for j in range(3):
                if state[i][j] == 0:
                    return i, j
        return -1, -1  # Không tìm thấy (không xảy ra với 8-puzzle hợp lệ)
    
    def _deep_copy(self, state):
        """Tạo bản sao sâu của một trạng thái."""
        return [row[:] for row in state]
    
    def _is_same_state(self, state1, state2):
        """Kiểm tra xem hai trạng thái có giống nhau không."""
        for i in range(3):
            for j in range(3):
                if state1[i][j] != state2[i][j]:
                    return False
        return True
    
    def _state_in_list(self, state, state_list):
        """Kiểm tra xem một trạng thái có trong danh sách trạng thái không."""
        for s in state_list:
            if self._is_same_state(state, s):
                return True
        return False
    
    def state_to_string(self, state):
        """Chuyển đổi trạng thái thành chuỗi để hiển thị."""
        result = ""
        for row in state:
            result += str(row) + "\n"
        return result
    
    def belief_state_to_string(self, belief_state):
        """Chuyển đổi belief state thành chuỗi để hiển thị."""
        result = f"Belief State (gồm {len(belief_state)} trạng thái):\n"
        for i, state in enumerate(belief_state):
            result += f"State {i+1}:\n"
            result += self.state_to_string(state)
            result += "\n"
        return result
