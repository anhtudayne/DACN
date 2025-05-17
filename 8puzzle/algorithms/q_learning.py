
import numpy as np
import random
import time
import copy
import tkinter as tk
from tkinter import Toplevel, Frame, Label, Button, BOTH
from tkinter import scrolledtext, ttk
from models.puzzle import Puzzle

class QLearning:
    """Thuật toán Q-learning cho bài toán 8-puzzle"""
    
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.3, goal_state=None):
        
        self.q_table = {}  # Bảng Q lưu giá trị Q(s,a)
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        
        # Trạng thái đích
        if goal_state is None:
            self.goal_state = [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 0]
            ]
        else:
            self.goal_state = goal_state
        
        # Thống kê huấn luyện
        self.episodes_completed = 0
        self.success_count = 0
        self.avg_steps = 0
        
    def get_state_key(self, state):
        """
        Chuyển đổi ma trận state thành tuple để làm khóa cho q_table
        
        Args:
            state (list): Ma trận 3x3 biểu diễn trạng thái
            
        Returns:
            tuple: Tuple biểu diễn trạng thái
        """
        return tuple(tuple(row) for row in state)
        
    def get_empty_position(self, state):
        """
        Tìm vị trí ô trống (giá trị 0) trong trạng thái
        
        Args:
            state (list): Ma trận 3x3 biểu diễn trạng thái
            
        Returns:
            tuple: Tọa độ (row, col) của ô trống
        """
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return (i, j)
        return None

    def get_valid_actions(self, state):
       
        # Tìm vị trí ô trống
        empty_pos = self.get_empty_position(state)
        
        # Xác định các hành động hợp lệ
        valid_actions = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # lên, phải, xuống, trái
        
        for action, (dx, dy) in enumerate(directions):
            new_x, new_y = empty_pos[0] + dx, empty_pos[1] + dy
            if 0 <= new_x < 3 and 0 <= new_y < 3:  # Kiểm tra biên
                valid_actions.append(action)
                
        return valid_actions, empty_pos

    def apply_action(self, state, action, empty_pos=None):
        """
        Áp dụng hành động lên trạng thái và trả về trạng thái mới
        
        Args:
            state (list): Trạng thái hiện tại
            action (int): Hành động (0: lên, 1: phải, 2: xuống, 3: trái)
            empty_pos (tuple, optional): Vị trí ô trống. Nếu None, sẽ tính toán.
            
        Returns:
            list: Trạng thái mới sau khi thực hiện hành động
        """
        # Tạo bản sao trạng thái
        new_state = [row[:] for row in state]
        
        # Tìm vị trí ô trống nếu chưa biết
        if empty_pos is None:
            empty_pos = self.get_empty_position(state)
        
        # Xác định hướng di chuyển
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # lên, phải, xuống, trái
        dx, dy = directions[action]
        
        # Vị trí mới của ô trống
        new_x, new_y = empty_pos[0] + dx, empty_pos[1] + dy
        
        # Đổi chỗ
        new_state[empty_pos[0]][empty_pos[1]] = new_state[new_x][new_y]
        new_state[new_x][new_y] = 0
        
        return new_state
        
    def get_reward(self, state, next_state):
        """
        Xác định phần thưởng khi chuyển từ trạng thái state sang next_state
        
        Args:
            state (list): Trạng thái hiện tại
            next_state (list): Trạng thái tiếp theo
            
        Returns:
            float: Giá trị phần thưởng
        """
        # Trạng thái đích có phần thưởng lớn
        if self.is_goal_state(next_state):
            return 100
        
        # Tính số ô đúng vị trí trước và sau hành động
        correct_tiles_before = self.count_correct_tiles(state)
        correct_tiles_after = self.count_correct_tiles(next_state)
        
        # Phần thưởng dựa trên sự thay đổi số ô đúng vị trí
        tile_diff = correct_tiles_after - correct_tiles_before
        
        # Tăng cường phần thưởng để khuyến khích các bước đi tốt
        if tile_diff > 0:
            return 10 * tile_diff  # Phần thưởng lớn hơn cho mỗi ô được đưa vào đúng vị trí
        elif tile_diff < 0:
            return -5 * abs(tile_diff)  # Phần phạt lớn hơn nếu làm tương trạng tài
        else:
            # Khuyến khích các bước tiến gần với trạng thái đích
            if correct_tiles_after >= 7:  # Nếu đã có nhiều ô đúng vị trí
                return 0  # Không phạt nặng
            
            return -1  # Phần thưởng âm nhỏ cho các bước không thay đổi số ô đúng
        
    def is_goal_state(self, state):
        """
        Kiểm tra xem trạng thái có phải là trạng thái đích không
        
        Args:
            state (list): Trạng thái cần kiểm tra
            
        Returns:
            bool: True nếu là trạng thái đích
        """
        return state == self.goal_state
        
    def count_correct_tiles(self, state):
        """
        Đếm số ô đúng vị trí so với trạng thái đích
        
        Args:
            state (list): Trạng thái cần kiểm tra
            
        Returns:
            int: Số ô đúng vị trí
        """
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] == self.goal_state[i][j]:
                    count += 1
        return count

    def choose_action(self, state):
        """
        Chọn hành động dựa trên chiến lược epsilon-greedy
        
        Args:
            state (list): Trạng thái hiện tại
            
        Returns:
            int: Hành động được chọn
            tuple: Vị trí ô trống
        """
        # Lấy các hành động hợp lệ
        valid_actions, empty_pos = self.get_valid_actions(state)
        
        if not valid_actions:
            return None, empty_pos
        
        # Chuyển trạng thái thành khóa để tra cứu trong bảng Q
        state_key = self.get_state_key(state)
        
        # Nếu trạng thái chưa có trong bảng Q, khởi tạo giá trị
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
            for a in range(4):  # 4 hành động có thể
                self.q_table[state_key][a] = 0.0
        
        # Chiến lược epsilon-greedy
        if random.random() < self.epsilon:  # Khám phá
            return random.choice(valid_actions), empty_pos
        else:  # Khai thác
            # Lấy giá trị Q cho các hành động hợp lệ
            q_values = [(action, self.q_table[state_key].get(action, 0.0)) 
                      for action in valid_actions]
            
            # Chọn hành động có giá trị Q cao nhất
            best_action = max(q_values, key=lambda x: x[1])[0]
            return best_action, empty_pos
    
    def update_q_value(self, state, action, reward, next_state):
        """
        Cập nhật giá trị Q cho cặp (trạng thái, hành động)
        
        Args:
            state (list): Trạng thái hiện tại
            action (int): Hành động được thực hiện
            reward (float): Phần thưởng nhận được
            next_state (list): Trạng thái tiếp theo
        """
        # Chuyển trạng thái thành khóa
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Khởi tạo nếu chưa có
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
            for a in range(4):
                self.q_table[state_key][a] = 0.0
                
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {}
            for a in range(4):
                self.q_table[next_state_key][a] = 0.0
        
        # Tính giá trị Q mới dựa trên công thức Q-learning
        # Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        old_value = self.q_table[state_key].get(action, 0.0)
        
        # Tìm giá trị Q lớn nhất cho trạng thái tiếp theo
        next_max = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
        
        # Tính giá trị mới
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        
        # Cập nhật vào bảng Q
        self.q_table[state_key][action] = new_value
    
    def create_initial_state(self, goal_state=None, shuffle_steps=20):
        """
        Tạo trạng thái ban đầu bằng cách xáo trộn trạng thái đích
        
        Args:
            goal_state (list, optional): Trạng thái đích của puzzle. Nếu None, sẽ dùng self.goal_state
            shuffle_steps (int): Số bước xáo trộn
            
        Returns:
            list: Trạng thái ban đầu sau khi xáo trộn
        """
        # Xác định trạng thái đích để xáo trộn
        if goal_state is None:
            goal_state = self.goal_state
            
        # Bắt đầu từ trạng thái đích
        state = [row[:] for row in goal_state]
        
        # Xáo trộn bằng cách di chuyển ngẫu nhiên
        for _ in range(shuffle_steps):
            valid_actions, empty_pos = self.get_valid_actions(state)
            if not valid_actions:
                break
                
            action = random.choice(valid_actions)
            state = self.apply_action(state, action, empty_pos)
            
        return state
    
    def train(self, initial_state=None, max_steps=100, status_callback=None):
        """
        Huấn luyện agent trên một trạng thái ban đầu
        
        Args:
            initial_state (list, optional): Trạng thái ban đầu cho tập huấn luyện. Nếu None, sẽ tạo ngẫu nhiên
            max_steps (int): Số bước tối đa cho mỗi episode
            status_callback (function, optional): Hàm callback để cập nhật tiến trình
            
        Returns:
            tuple: (thành công, số bước, trạng thái cuối, đường đi)
        """
        # Kiểm tra trạng thái ban đầu
        if initial_state is None:
            # Nếu không có trạng thái ban đầu, tạo một trạng thái ngẫu nhiên
            state = self.create_initial_state(self.goal_state, shuffle_steps=20)
        else:
            # Sử dụng trạng thái ban đầu được cung cấp
            state = [row[:] for row in initial_state]
        
        # Lưu lại đường đi
        path = [state]
        steps = 0
        
        # Nếu trạng thái ban đầu là trạng thái đích, trả về luôn
        if self.is_goal_state(state):
            return True, 0, state, path
        
        # Thông báo bắt đầu huấn luyện
        if status_callback:
            status_callback(f"Bắt đầu huấn luyện một tập từ trạng thái ban đầu...")
        
        # Huấn luyện trên trạng thái ban đầu đã cho
        while steps < max_steps:
            # Chọn hành động dựa trên chiến lược epsilon-greedy
            action, empty_pos = self.choose_action(state)
            
            # Kiểm tra nếu không có hành động hợp lệ
            if action is None:
                if status_callback:
                    status_callback("Không có hành động hợp lệ từ trạng thái này!")
                return False, steps, state, path
            
            # Thực hiện hành động
            next_state = self.apply_action(state, action, empty_pos)
            
            # Xác định phần thưởng
            reward = self.get_reward(state, next_state)
            
            # Cập nhật giá trị Q
            self.update_q_value(state, action, reward, next_state)
            
            # Lưu trạng thái mới vào đường đi
            path.append(next_state)
            
            # Cập nhật trạng thái hiện tại
            state = next_state
            steps += 1
            
            # Cập nhật tiến trình
            if status_callback and steps % 10 == 0:
                status_callback(f"Bước huấn luyện {steps}/{max_steps}")
            
            # Kiểm tra xem đã đạt trạng thái đích chưa
            if self.is_goal_state(state):
                if status_callback:
                    status_callback(f"Đã tìm được trạng thái đích sau {steps} bước!")
                return True, steps, state, path
        
        # Nếu không tìm được trạng thái đích trong số bước tối đa
        if status_callback:
            status_callback(f"Không tìm được trạng thái đích sau {max_steps} bước!")
        
        return False, steps, state, path
    
    def solve(self, initial_state, visualization_callback=None, status_callback=None, delay=0.5):
        """
        Giải quyết puzzle bằng cách sử dụng bảng Q đã học
        
        Args:
            initial_state (list): Trạng thái ban đầu của puzzle
            visualization_callback (function, optional): Hàm cập nhật hiển thị trực quan
            status_callback (function, optional): Hàm cập nhật trạng thái
            delay (float): Thời gian trễ giữa các bước (giây)
            
        Returns:
            tuple: (thành công, số bước, trạng thái cuối cùng, đường đi)
        """
        # Sẽ dùng epsilon = 0 để luôn chọn hành động tốt nhất đã học
        original_epsilon = self.epsilon
        self.epsilon = 0
        
        # Bắt đầu từ trạng thái ban đầu
        state = [row[:] for row in initial_state]
        
        # Trả về ngay nếu đã ở trạng thái đích
        if self.is_goal_state(state):
            if status_callback:
                status_callback("Đã ở trạng thái đích!")
            return True, 0, state, [state]
        
        # Giới hạn số bước - tăng lên để có nhiều cơ hội tìm được giải pháp
        max_steps = 200
        steps = 0
        path = []
        
        # Lưu lại trạng thái ban đầu
        path.append(state)
        
        # Cập nhật hiển thị ban đầu
        if visualization_callback:
            visualization_callback(state)
            
        if status_callback:
            status_callback(f"Bắt đầu giải puzzle với Q-learning (bảng Q có {len(self.q_table)} trạng thái)")
        
        # Lưu trữ các trạng thái đã xét để tránh lặp
        visited_states = set()
        visited_states.add(self.get_state_key(state))
        
        # Lặp qua các bước
        while steps < max_steps:
            # Chọn hành động tốt nhất dựa trên bảng Q
            action, empty_pos = self.choose_action(state)
            
            # Nếu không có hành động hợp lệ
            if action is None:
                if status_callback:
                    status_callback("\nKhông có hành động hợp lệ!")
                self.epsilon = original_epsilon
                return False, steps, state, path
            
            # Kiểm tra xem trạng thái có trong bảng Q không
            state_key = self.get_state_key(state)
            if state_key not in self.q_table:
                # Nếu trạng thái chưa có trong bảng Q, khởi tạo nó
                self.q_table[state_key] = {}
                for a in range(4):
                    self.q_table[state_key][a] = 0.0
                    
                # Nếu không có giá trị nào trong bảng Q, thử huấn luyện từ trạng thái này
                if status_callback:
                    status_callback("\nTrạng thái chưa được học, thử huấn luyện từ trạng thái này...")
                    
                # Tạm thời đặt epsilon về giá trị cao để khám phá
                temp_epsilon = self.epsilon
                self.epsilon = 0.9
                
                # Huấn luyện nhanh từ trạng thái hiện tại
                success, train_steps, final_state, train_path = self.train(state, max_steps=50)
                
                # Khôi phục epsilon
                self.epsilon = temp_epsilon
                
                # Nếu huấn luyện thành công, tiếp tục với giá trị Q mới
                if not success:
                    if status_callback:
                        status_callback("\nKhông thể huấn luyện từ trạng thái này!")
                    self.epsilon = original_epsilon
                    return False, steps, state, path
            
            # Thực hiện hành động
            next_state = self.apply_action(state, action, empty_pos)
            next_state_key = self.get_state_key(next_state)
            
            # Kiểm tra xem đã xét trạng thái này chưa để tránh vòng lặp
            if next_state_key in visited_states:
                # Thử chọn hành động khác ngẫu nhiên để thoát khỏi vòng lặp
                valid_actions, _ = self.get_valid_actions(state)
                valid_actions = [a for a in valid_actions if a != action]  # Loại bỏ hành động vừa chọn
                
                if not valid_actions:
                    if status_callback:
                        status_callback("\nBị kẹt trong vòng lặp trạng thái và không có hành động thay thế!")
                    self.epsilon = original_epsilon
                    return False, steps, state, path
                    
                # Chọn hành động khác ngẫu nhiên
                action = random.choice(valid_actions)
                next_state = self.apply_action(state, action, empty_pos)
                next_state_key = self.get_state_key(next_state)
            
            # Cập nhật trạng thái đã xét
            visited_states.add(next_state_key)
            
            # Cập nhật trạng thái và hiện thị
            directions = ["lên", "phải", "xuống", "trái"]
            if status_callback:
                status_callback(f"Bước {steps+1}: Di chuyển {directions[action]}")
            
            # Lưu vào đường đi
            state = next_state
            path.append(state)
            steps += 1
            
            # Cập nhật hiển thị
            if visualization_callback:
                visualization_callback(state)
                time.sleep(delay)
            
            # Kiểm tra nếu đã đạt đến trạng thái đích
            if self.is_goal_state(state):
                if status_callback:
                    status_callback(f"\nĐã tìm thấy trạng thái đích sau {steps} bước!")
                # Khôi phục epsilon
                self.epsilon = original_epsilon
                return True, steps, state, path
        
        # Quá số bước tối đa
        if status_callback:
            status_callback(f"\nKhông tìm được giải pháp trong {max_steps} bước!")
        
        # Khôi phục epsilon
        self.epsilon = original_epsilon
        return False, steps, state, path


def show_qlearning_visualization(initial_state, goal_state, learning_params=None):
    """
    Hiển thị cửa sổ trực quan hóa Q-learning với tiến trình huấn luyện tích hợp
        
    Args:
        initial_state: Trạng thái bài toán cần giải quyết
        goal_state: Trạng thái đích của bài toán
        learning_params: Thông số huấn luyện tùy chỉnh (tùy chọn)
    """
    # Thiết lập các tham số huấn luyện mặc định
    if learning_params is None:
        learning_params = {
            "alpha": 0.1,  # Learning rate
            "gamma": 0.9,  # Discount factor
            "epsilon": 0.3,  # Exploration rate
            "episodes": 1000,  # Số lượt huấn luyện
            "shuffle_steps": 20  # Số bước trộn cho mỗi trạng thái ban đầu mới
        }
        
    # Tạo một trạng thái ban đầu gần với đích nhưng không phải là đích
    # Nếu initial_state đang trống hoặc đúng với goal_state
    if initial_state == goal_state or all(initial_state[i][j] == 0 for i in range(3) for j in range(3)):
        # Tạo trạng thái gần với đích: đảo vị trí 2 số cuối cùng
        initial_state = [row[:] for row in goal_state]
        # Tìm vị trí của 0 (ô trống)
        empty_i, empty_j = None, None
        for i in range(3):
            for j in range(3):
                if initial_state[i][j] == 0:
                    empty_i, empty_j = i, j
        
        # Nếu ô trống không ở cuối, đổi vị trí 2 ô cuối cùng
        if empty_i != 2 or empty_j != 2:
            initial_state[2][1], initial_state[2][2] = initial_state[2][2], initial_state[2][1]
        else:
            # Nếu ô trống ở cuối, đổi vị trí 2 ô khác
            initial_state[2][0], initial_state[1][2] = initial_state[1][2], initial_state[2][0]
    
    # Tạo cửa sổ mới
    window = Toplevel()
    window.title("Q-Learning - 8 Puzzle")
    window.state('zoomed')  # Toàn màn hình
    window.minsize(800, 600)
    window.focus_set()
    
    # Frame chính
    main_frame = Frame(window, padx=20, pady=20)
    main_frame.pack(fill=BOTH, expand=True)
    
    # Tiêu đề và mô tả
    title_frame = Frame(main_frame, bg="#e3f2fd")
    title_frame.pack(pady=10, fill="x")
    
    Label(title_frame, text="Thuật toán Q-Learning", 
          font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#01579b").pack(pady=5)
    Label(title_frame, text="Học tăng cường (Reinforcement Learning) với bài toán 8-puzzle",
          font=("Arial", 10), bg="#e3f2fd", fg="#0277bd").pack(pady=2)
    
    # Hiển thị thông tin huấn luyện
    info_frame = Frame(main_frame, bg="#e8eaf6", relief="groove", borderwidth=1)
    info_frame.pack(pady=5, fill="x", padx=10)
    
    # Tạo lưới hiển thị thông số
    param_frame = Frame(info_frame, bg="#e8eaf6")
    param_frame.pack(pady=10, fill="x")
    
    # Cột 1: Thông số huấn luyện
    col1 = Frame(param_frame, bg="#e8eaf6")
    col1.pack(side="left", padx=20)
    
    Label(col1, text="Thông số huấn luyện:", 
          font=("Arial", 10, "bold"), bg="#e8eaf6").pack(anchor="w")
    alpha_label = Label(col1, text=f"Learning rate (α): {learning_params['alpha']:.2f}", 
          font=("Arial", 10), bg="#e8eaf6")
    alpha_label.pack(anchor="w")
    gamma_label = Label(col1, text=f"Discount factor (γ): {learning_params['gamma']:.2f}", 
          font=("Arial", 10), bg="#e8eaf6")
    gamma_label.pack(anchor="w")
    epsilon_label = Label(col1, text=f"Exploration rate (ε): {learning_params['epsilon']:.2f}", 
          font=("Arial", 10), bg="#e8eaf6")
    epsilon_label.pack(anchor="w")
    
    # Cột 2: Tiến trình và kết quả huấn luyện
    col2 = Frame(param_frame, bg="#e8eaf6")
    col2.pack(side="left", padx=20)
    
    # Tiêu đề tiến trình huấn luyện
    training_status_label = Label(col2, text="Đang chuẩn bị huấn luyện...", 
          font=("Arial", 10, "bold"), bg="#e8eaf6", fg="#01579b")
    training_status_label.pack(anchor="w")
    
    # Số episodes và thông tin huấn luyện
    episodes_label = Label(col2, text=f"Số episodes: 0/{learning_params['episodes']}", 
          font=("Arial", 10), bg="#e8eaf6")
    episodes_label.pack(anchor="w")
    
    # Trạng thái huấn luyện
    success_rate_label = Label(col2, text="Tỷ lệ thành công: 0.0%", 
          font=("Arial", 10), bg="#e8eaf6")
    success_rate_label.pack(anchor="w")
    
    avg_steps_label = Label(col2, text="Số bước trung bình: 0.0", 
          font=("Arial", 10), bg="#e8eaf6")
    avg_steps_label.pack(anchor="w")
    
    # Thanh tiến trình huấn luyện
    progress_frame = Frame(info_frame, bg="#e8eaf6")
    progress_frame.pack(pady=5, fill="x", padx=20)
    
    progress_label = Label(progress_frame, text="Tiến trình huấn luyện:", 
          font=("Arial", 10), bg="#e8eaf6")
    progress_label.pack(anchor="w")
    
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=5, fill="x")
    
    # Frame cho trạng thái và kết quả
    content_frame = Frame(main_frame)
    content_frame.pack(pady=10, fill="both", expand=True)
    
    # Frame cho puzzle
    puzzle_frame = Frame(content_frame)
    puzzle_frame.pack(side="left", padx=10, fill="y")
    
    Label(puzzle_frame, text="Trạng thái hiện tại:", 
          font=("Arial", 11, "bold")).pack(pady=5)
    
    # Grid hiển thị puzzle
    puzzle_grid = Frame(puzzle_frame)
    puzzle_grid.pack(pady=10)
    
    cell_labels = []
    for i in range(3):
        row_labels = []
        for j in range(3):
            cell_frame = Frame(puzzle_grid, borderwidth=2, relief="raised", 
                            width=70, height=70, bg="#f5f5f5")
            cell_frame.grid(row=i, column=j, padx=3, pady=3)
            cell_frame.pack_propagate(False)  # Giữ kích thước cố định
            
            label = Label(cell_frame, text=" ", 
                       font=("Arial", 16, "bold"), bg="#f5f5f5")
            label.pack(expand=True)
            
            row_labels.append(label)
        cell_labels.append(row_labels)
    
    # Frame cho log và các nút
    log_frame = Frame(content_frame)
    log_frame.pack(side="right", padx=10, fill="both", expand=True)
    
    # Tiêu đề log
    Label(log_frame, text="Quá trình giải quyết:", 
          font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
    
    # Tạo text area hiển thị log
    log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                      font=("Courier", 10))
    log_text.pack(fill="both", expand=True, pady=5)
    log_text.insert("end", "Bắt đầu giải quyết puzzle với Q-learning...\n")
    log_text.config(state="disabled")
    
    # Frame cho các nút
    button_frame = Frame(main_frame)
    button_frame.pack(pady=10)
    
    def update_visualization(state, agent_goal_state=None):
        """Cập nhật hiển thị puzzle"""
        goal = agent_goal_state if agent_goal_state is not None else goal_state
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                text = str(value) if value != 0 else " "
                
                # Kiểm tra xem ô có đúng vị trí so với trạng thái đích không
                is_correct = (value == goal[i][j])
                
                # Cập nhật text và màu sắc
                cell_labels[i][j].config(
                    text=text,
                    fg="green" if is_correct else "black",
                    bg="#e8f5e9" if is_correct else "#f5f5f5"
                )
        
        # Cập nhật giao diện
        window.update()
    
    def update_log(message):
        """Cập nhật log với thông điệp mới"""
        log_text.config(state="normal")
        log_text.insert("end", message + "\n")
        log_text.see("end")  # Cuộn xuống cuối
        log_text.config(state="disabled")
        window.update()
    
    # Biến cho đối tượng agent
    agent_var = {"instance": None}
    training_stats_var = {"success_count": 0, "total_steps": 0, "episode_count": 0}
    
    def start_training():
        """Bắt đầu quá trình huấn luyện"""
        # Xóa log cũ
        log_text.config(state="normal")
        log_text.delete(1.0, "end")
        log_text.insert("end", "Bắt đầu huấn luyện thuật toán Q-learning...\n")
        log_text.config(state="disabled")
        
        # Vô hiệu hóa các nút trong quá trình huấn luyện
        start_training_button.config(state="disabled")
        solve_button.config(state="disabled")
        close_button.config(state="disabled")
        
        # Cập nhật trạng thái huấn luyện
        training_status_label.config(text="Đang huấn luyện...")
        
        # Khởi tạo agent
        agent_var["instance"] = QLearning(
            learning_rate=learning_params["alpha"],
            discount_factor=learning_params["gamma"],
            exploration_rate=learning_params["epsilon"],
            goal_state=goal_state
        )
        
        # Reset tiến trình
        progress_bar["value"] = 0
        training_stats_var["success_count"] = 0
        training_stats_var["total_steps"] = 0
        training_stats_var["episode_count"] = 0
        
        # Bắt đầu huấn luyện trong một thread riêng
        import threading
        thread = threading.Thread(target=training_process, daemon=True)
        thread.start()
    
    def training_process():
        """Tiến trình huấn luyện"""
        agent = agent_var["instance"]
        episodes = learning_params["episodes"]
        shuffle_steps = learning_params["shuffle_steps"]
        
        for i in range(episodes):
            # Cập nhật tiến trình
            progress_bar["value"] = (i / episodes) * 100
            episodes_label.config(text=f"Số episodes: {i}/{episodes}")
            training_stats_var["episode_count"] = i
            
            # Tạo trạng thái ban đầu
            episode_initial = agent.create_initial_state(goal_state, shuffle_steps)
            
            # Huấn luyện một tập
            success, steps, _, _ = agent.train(episode_initial)
            
            if success:
                training_stats_var["success_count"] += 1
                training_stats_var["total_steps"] += steps
            
            # Cập nhật thống kê
            if training_stats_var["success_count"] > 0:
                success_rate = (training_stats_var["success_count"] / (i+1)) * 100
                avg_steps = training_stats_var["total_steps"] / training_stats_var["success_count"]
                success_rate_label.config(text=f"Tỷ lệ thành công: {success_rate:.1f}%")
                avg_steps_label.config(text=f"Số bước trung bình: {avg_steps:.1f}")
            
            # Cập nhật giao diện
            window.update()
        
        # Hoàn thành huấn luyện
        progress_bar["value"] = 100
        training_status_label.config(text="Đã hoàn thành huấn luyện!")
        episodes_label.config(text=f"Số episodes: {episodes}/{episodes}")
        
        # Danh sách các trạng thái ban đầu cố định với độ khó tăng dần
        fixed_states = [
            # Dễ (2-3 bước)
            [
                [1, 2, 3],
                [4, 5, 0],
                [7, 8, 6]
            ],
            # Vừa phải (5-7 bước)
            [
                [1, 2, 3],
                [4, 0, 6],
                [7, 5, 8]
            ],
            # Khó (8-12 bước)
            [
                [1, 2, 3],
                [0, 4, 6],
                [7, 5, 8]
            ],
        ]
        
        # Chọn trạng thái dễ (index 0)
        selected_state = fixed_states[0]  # Mức độ dễ (2-3 bước)
        
        # Cập nhật hiển thị trạng thái ban đầu lên bảng
        update_visualization(selected_state)
        
        # Thêm log
        log_text.config(state="normal")
        log_text.insert("end", "\n\nĐã hoàn thành quá trình huấn luyện!\n")
        success_rate = (training_stats_var["success_count"] / episodes) * 100
        log_text.insert("end", f"Tỷ lệ thành công: {success_rate:.1f}%\n")
        if training_stats_var["success_count"] > 0:
            avg_steps = training_stats_var["total_steps"] / training_stats_var["success_count"]
            log_text.insert("end", f"Số bước trung bình: {avg_steps:.1f}\n")
        log_text.insert("end", "\nBạn có thể bắt đầu giải quyết puzzle bằng nút 'Giải Puzzle'\n")
        log_text.config(state="disabled")
        
        # Kích hoạt lại các nút
        start_training_button.config(state="normal")
        solve_button.config(state="normal")
        close_button.config(state="normal")
    
    def start_solving():
        """Bắt đầu giải quyết puzzle"""
        agent = agent_var["instance"]
        if agent is None:
            update_log("Bạn cần huấn luyện trước khi giải quyết puzzle!")
            return
            
        # Tạo trạng thái ban đầu nếu bảng trống
        # Kiểm tra xem có số trên bảng hay không
        has_numbers = False
        for i in range(3):
            for j in range(3):
                if cell_labels[i][j].cget("text").strip() != "":
                    has_numbers = True
                    break
        
        # Nếu không có số hiển thị, sử dụng trạng thái cố định để bắt đầu
        if not has_numbers:
            # Danh sách các trạng thái ban đầu cố định với độ khó tăng dần
            fixed_states = [
                # Dễ (2-3 bước)
                [
                    [1, 2, 3],
                    [4, 5, 0],
                    [7, 8, 6]
                ],
                # Vừa phải (5-7 bước)
                [
                    [1, 2, 3],
                    [4, 0, 6],
                    [7, 5, 8]
                ],
                # Khó (8-12 bước)
                [
                    [1, 2, 3],
                    [0, 4, 6],
                    [7, 5, 8]
                ],
            ]
            
            # Chọn trạng thái dễ (index 0)
            selected_state = fixed_states[0]  # Mức độ dễ (2-3 bước)
            update_visualization(selected_state)
        
        # Xóa log cũ
        log_text.config(state="normal")
        log_text.delete(1.0, "end")
        log_text.insert("end", "Bắt đầu giải quyết puzzle với thuật toán Q-learning...\n")
        log_text.config(state="disabled")
        
        # Vô hiệu hóa nút giải quyết
        solve_button.config(state="disabled")
        start_training_button.config(state="disabled")
        
        # Đọc trạng thái hiện tại từ bảng hiển thị
        current_state = []
        for i in range(3):
            row = []
            for j in range(3):
                value = cell_labels[i][j].cget("text").strip()
                if value == "":
                    row.append(0)  # Ô trống
                else:
                    row.append(int(value))
            current_state.append(row)
        
        # Giải quyết puzzle với trạng thái hiện tại
        update_log("Bắt đầu giải puzzle với trạng thái ban đầu:")
        # Hiển thị trạng thái ban đầu ở dạng ma trận
        for row in current_state:
            update_log(str(row))
            
        # Đảm bảo bảng Q đã được khởi tạo với một số trạng thái ban đầu
        if len(agent.q_table) == 0:
            update_log("\nPhát hiện bảng Q trống, đang khởi tạo với một số trạng thái...")
            # Tạo một số trạng thái cơ bản và thêm vào bảng Q
            # Tạo và huấn luyện trạng thái hiện tại
            state_key = agent.get_state_key(current_state)
            agent.q_table[state_key] = {}
            for a in range(4):
                agent.q_table[state_key][a] = 0.0
                
            # Thực hiện 100 bước huấn luyện nhanh
            success, _, _, _ = agent.train(current_state, max_steps=100)
            update_log("Huấn luyện nhanh hoàn tất. Bảng Q hiện có " + str(len(agent.q_table)) + " trạng thái.")
        else:
            update_log("\nSử dụng bảng Q đã học với " + str(len(agent.q_table)) + " trạng thái")
            
        update_log("Bắt đầu tìm kiếm đường đi đến trạng thái đích...\n")
            
        # Tăng thời gian trễ để dễ theo dõi hơn
        success, steps, final_state, path = agent.solve(
            current_state, 
            visualization_callback=lambda state: update_visualization(state, agent.goal_state), 
            status_callback=update_log,
            delay=1.5  # Tăng thời gian trễ lên 1.5 giây để dễ quan sát
        )
        
        # Hiển thị kết quả
        if success:
            update_log(f"\nĐã giải quyết thành công puzzle sau {steps} bước!")
        else:
            update_log(f"\nKhông tìm được giải pháp cho puzzle này!")
            update_log("Có thể bảng Q chưa được huấn luyện đủ hoặc trạng thái quá phức tạp.")
        
        # Kích hoạt lại các nút
        solve_button.config(state="normal")
        start_training_button.config(state="normal")
    
    # Nút huấn luyện
    start_training_button = Button(button_frame, text="Huấn luyện Model", 
                         command=start_training,
                         font=("Arial", 11, "bold"), 
                         bg="#2196F3", fg="white",
                         relief="raised", borderwidth=2,
                         padx=15, pady=6)
    start_training_button.pack(side="left", padx=10)
    
    # Nút giải quyết
    solve_button = Button(button_frame, text="Giải Puzzle", 
                         command=start_solving,
                         font=("Arial", 11, "bold"), 
                         bg="#4CAF50", fg="white",
                         relief="raised", borderwidth=2,
                         padx=15, pady=6)
    solve_button.pack(side="left", padx=10)
    solve_button.config(state="disabled")  # Vô hiệu hóa cho đến khi huấn luyện xong
    
    # Nút đóng
    close_button = Button(button_frame, text="Đóng", 
                         command=window.destroy,
                         font=("Arial", 11), 
                         bg="#f44336", fg="white",
                         relief="raised", borderwidth=2,
                         padx=15, pady=6)
    close_button.pack(side="left", padx=10)
    
    # Hiển thị trạng thái ban đầu
    update_visualization(initial_state)
    
    # Cập nhật UI
    window.mainloop()
