
import copy

class PartialObservationPuzzle:
   
    
    def __init__(self, known_tile_position, known_tile_value):
      
        self.known_tile_position = known_tile_position  # (row, col)
        self.known_tile_value = known_tile_value
        
        # Khởi tạo các goal states dựa trên ô đã biết
        self.goal_states = self._generate_goal_states()
    
    def get_initial_belief_state(self):
        """Lấy initial belief state (5 trạng thái cố định)."""
        # Sử dụng 5 trạng thái đại diện cố định
        return [
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 0]
            ],
            [
                [1, 2, 3],
                [4, 0, 6],
                [7, 5, 8]
            ],
            [
                [1, 2, 3],
                [0, 4, 6],
                [7, 5, 8]
            ],
            [
                [0, 2, 3],
                [1, 4, 6],
                [7, 5, 8]
            ],
            [
                [1, 0, 3],
                [4, 2, 6],
                [7, 5, 8]
            ]
        ]
    
    def _generate_goal_states(self):
        """
        Tạo các goal states dựa trên ô đã biết.
        Mỗi goal state được tạo ra sẽ có ô đã biết ở đúng vị trí và giá trị.
        """
        # Bắt đầu với một mẫu trạng thái goal chuẩn 
        # (ô 1 ở vị trí [0,0], ô 2 ở [0,1], ..., ô 0 (ô trống) ở [2,2])
        template = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        
        # Vị trí và giá trị đã biết
        row, col = self.known_tile_position
        value = self.known_tile_value
        
        # Kiểm tra xem vị trí đã biết có đúng với template không
        if template[row][col] == value:
            # Nếu đúng, template hiện tại là một goal state
            goal_states = [copy.deepcopy(template)]
            
            # Tạo thêm 4 biến thể khác của goal state bằng cách hoán đổi một số vị trí
            # nhưng vẫn đảm bảo ô đã biết không thay đổi
            variants = []
            
            # Biến thể 1: Đổi chỗ hai ô không bao gồm ô đã biết và ô trống
            variant1 = copy.deepcopy(template)
            # Tìm 2 vị trí không phải là vị trí đã biết và không phải ô trống
            pos1, pos2 = self._find_two_positions_to_swap(template, row, col)
            r1, c1 = pos1
            r2, c2 = pos2
            variant1[r1][c1], variant1[r2][c2] = variant1[r2][c2], variant1[r1][c1]
            variants.append(variant1)
            
            # Biến thể 2: Đổi chỗ hai ô khác
            variant2 = copy.deepcopy(template)
            pos3, pos4 = self._find_two_other_positions_to_swap(template, row, col, pos1, pos2)
            r3, c3 = pos3
            r4, c4 = pos4
            variant2[r3][c3], variant2[r4][c4] = variant2[r4][c4], variant2[r3][c3]
            variants.append(variant2)
            
            # Biến thể 3: Kết hợp cả hai sự hoán đổi trên
            variant3 = copy.deepcopy(variant1)
            variant3[r3][c3], variant3[r4][c4] = variant3[r4][c4], variant3[r3][c3]
            variants.append(variant3)
            
            # Biến thể 4: Di chuyển ô trống
            variant4 = copy.deepcopy(template)
            empty_row, empty_col = 2, 2  # Vị trí ô trống trong template
            if (empty_row, empty_col) != (row, col):
                # Tìm một vị trí kề với ô trống để hoán đổi
                # nhưng không phải vị trí đã biết
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_r, new_c = empty_row + dr, empty_col + dc
                    if 0 <= new_r < 3 and 0 <= new_c < 3 and (new_r, new_c) != (row, col):
                        variant4[empty_row][empty_col], variant4[new_r][new_c] = variant4[new_r][new_c], variant4[empty_row][empty_col]
                        break
            variants.append(variant4)
            
            # Thêm các biến thể vào danh sách goal states
            goal_states.extend(variants)
            
            return goal_states
        else:
            # Nếu vị trí đã biết khác với template, tạo một goal state mới
            # bằng cách hoán đổi vị trí trong template
            custom_goal = copy.deepcopy(template)
            
            # Tìm vị trí hiện tại của giá trị cần đặt
            current_pos = None
            for r in range(3):
                for c in range(3):
                    if custom_goal[r][c] == value:
                        current_pos = (r, c)
                        break
                if current_pos:
                    break
            
            # Hoán đổi vị trí để đặt giá trị đúng chỗ
            custom_goal[current_pos[0]][current_pos[1]], custom_goal[row][col] = custom_goal[row][col], custom_goal[current_pos[0]][current_pos[1]]
            
            # Tạo 5 goal states: 1 chuẩn và 4 biến thể
            goal_states = [custom_goal]
            
            # Tạo 4 biến thể tương tự như trên
            # ...
            # (Để đơn giản, chúng ta sẽ tạo các biến thể bằng cách hoán đổi ngẫu nhiên)
            for _ in range(4):
                variant = copy.deepcopy(custom_goal)
                # Tìm 2 vị trí không phải là vị trí đã biết và không phải ô trống
                pos1, pos2 = self._find_two_positions_to_swap(variant, row, col)
                r1, c1 = pos1
                r2, c2 = pos2
                variant[r1][c1], variant[r2][c2] = variant[r2][c2], variant[r1][c1]
                goal_states.append(variant)
            
            return goal_states
    
    def _find_two_positions_to_swap(self, state, known_row, known_col):
        """Tìm hai vị trí không phải là vị trí đã biết và không phải ô trống để hoán đổi."""
        positions = []
        for r in range(3):
            for c in range(3):
                if (r, c) != (known_row, known_col) and state[r][c] != 0:
                    positions.append((r, c))
                    if len(positions) == 2:
                        return positions
        return positions
    
    def _find_two_other_positions_to_swap(self, state, known_row, known_col, pos1, pos2):
        """Tìm hai vị trí khác để hoán đổi."""
        positions = []
        for r in range(3):
            for c in range(3):
                if (r, c) != (known_row, known_col) and (r, c) != pos1 and (r, c) != pos2 and state[r][c] != 0:
                    positions.append((r, c))
                    if len(positions) == 2:
                        return positions
        return positions
    
    def get_actions(self, belief_state):
        """
        Lấy danh sách các hành động có thể thực hiện từ belief state hiện tại.
        
        Args:
            belief_state (list): Tập hợp các trạng thái có thể.
            
        Returns:
            list: Danh sách các hành động có thể thực hiện.
        """
        # Trong 8-puzzle, các hành động luôn là UP, DOWN, LEFT, RIGHT
        # nhưng chỉ áp dụng những hành động hợp lệ trên ít nhất một trạng thái
        actions = []
        for action in ["UP", "DOWN", "LEFT", "RIGHT"]:
            for state in belief_state:
                new_state = self._apply_action_to_state(state, action)
                if new_state:
                    actions.append(action)
                    break
        return actions
    
    def _apply_action_to_state(self, state, action):
        """
        Áp dụng một hành động lên một trạng thái cụ thể.
        
        Args:
            state (list): Trạng thái hiện tại.
            action (str): Hành động cần áp dụng.
            
        Returns:
            list: Trạng thái mới sau khi áp dụng hành động, hoặc None nếu hành động không hợp lệ.
        """
        # Sao chép trạng thái để không làm thay đổi trạng thái ban đầu
        new_state = copy.deepcopy(state)
        
        # Tìm vị trí ô trống (0)
        empty_pos = None
        for r in range(3):
            for c in range(3):
                if new_state[r][c] == 0:
                    empty_pos = (r, c)
                    break
            if empty_pos:
                break
        
        # Thực hiện hành động
        r, c = empty_pos
        if action == "UP" and r > 0:
            # Di chuyển ô trên xuống dưới
            new_state[r][c], new_state[r-1][c] = new_state[r-1][c], new_state[r][c]
            return new_state
        elif action == "DOWN" and r < 2:
            # Di chuyển ô dưới lên trên
            new_state[r][c], new_state[r+1][c] = new_state[r+1][c], new_state[r][c]
            return new_state
        elif action == "LEFT" and c > 0:
            # Di chuyển ô trái sang phải
            new_state[r][c], new_state[r][c-1] = new_state[r][c-1], new_state[r][c]
            return new_state
        elif action == "RIGHT" and c < 2:
            # Di chuyển ô phải sang trái
            new_state[r][c], new_state[r][c+1] = new_state[r][c+1], new_state[r][c]
            return new_state
        else:
            # Hành động không hợp lệ
            return None
    
    def apply_action(self, belief_state, action):
        """
        Áp dụng một hành động lên belief state và lọc các trạng thái không hợp lệ.
        
        Args:
            belief_state (list): Belief state hiện tại.
            action (str): Hành động cần áp dụng.
            
        Returns:
            list: Belief state mới sau khi áp dụng hành động.
        """
        new_belief_state = []
        for state in belief_state:
            new_state = self._apply_action_to_state(state, action)
            if new_state and self._is_consistent_with_observation(new_state):
                # Kiểm tra trùng lặp
                if not any(self._states_equal(new_state, existing_state) for existing_state in new_belief_state):
                    new_belief_state.append(new_state)
        return new_belief_state
    
    def _is_consistent_with_observation(self, state):
        """
        Kiểm tra xem trạng thái có phù hợp với observation không.
        Trong trường hợp này, observation là biết trước một ô trong goal state.
        
        Args:
            state (list): Trạng thái cần kiểm tra.
            
        Returns:
            bool: True nếu trạng thái phù hợp với observation, False nếu không.
        """
        # Trong quá trình tìm kiếm, tất cả các trạng thái đều hợp lệ
        # vì chúng ta chỉ kiểm tra goal states
        return True
    
    def _states_equal(self, state1, state2):
        """Kiểm tra hai trạng thái có bằng nhau không."""
        for r in range(3):
            for c in range(3):
                if state1[r][c] != state2[r][c]:
                    return False
        return True
    
    def is_goal(self, belief_state):
        """
        Kiểm tra xem belief state có đạt mục tiêu không.
        Một belief state đạt mục tiêu khi tất cả các trạng thái trong đó đều là goal states.
        
        Args:
            belief_state (list): Belief state cần kiểm tra.
            
        Returns:
            bool: True nếu belief state đạt mục tiêu, False nếu không.
        """
        # Kiểm tra từng trạng thái trong belief state
        for state in belief_state:
            # Kiểm tra xem state có phải là một trong các goal states không
            is_goal_state = False
            for goal_state in self.goal_states:
                if self._states_equal(state, goal_state):
                    is_goal_state = True
                    break
            
            # Nếu có một trạng thái không phải goal state, trả về False
            if not is_goal_state:
                return False
        
        # Nếu tất cả các trạng thái đều là goal states, trả về True
        return True
    
    def belief_state_to_string(self, belief_state):
        """
        Chuyển đổi belief state thành chuỗi để hiển thị.
        
        Args:
            belief_state (list): Belief state cần chuyển đổi.
            
        Returns:
            str: Chuỗi biểu diễn belief state.
        """
        result = f"Belief State (gồm {len(belief_state)} trạng thái):\n"
        for i, state in enumerate(belief_state):
            result += f"State {i+1}:\n"
            for row in state:
                result += str(row) + "\n"
            result += "\n"
        return result
