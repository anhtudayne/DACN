import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import copy

from models.sensorless_puzzle import SensorlessPuzzle
from algorithms.sensorless_search import SensorlessSearch

class SensorlessSearchWindow:
   
    
    def __init__(self, parent):
        """
        Khởi tạo cửa sổ tìm kiếm sensorless.
        
        Args:
            parent: Widget cha (main window)
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Search with No Observation")
        self.window.geometry("1300x850")  # Tăng kích thước cử a sổ một chút
        
        # Khởi tạo puzzle và search
        self.puzzle = SensorlessPuzzle()
        self.search = SensorlessSearch(self.puzzle)
        
        # Biến để lưu trữ kết quả
        self.solution_path = None
        self.current_step = 0
        self.current_belief_state = None
        
        # Tạo giao diện
        self._create_widgets()
        
        # Hiển thị initial belief state
        self._display_initial_state()
        
        # Hiển thị goal states
        self._display_goal_states()
    
    def _create_widgets(self):
        """Tạo các widget trên giao diện."""
        # Frame chính
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chia làm 2 phần: trái và phải
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_frame.config(width=600)  # Đặt chiều rộng cụ thể cho frame bên trái
        
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame hiển thị belief states (bên trái)
        belief_state_frame = ttk.LabelFrame(left_frame, text="Belief States")
        belief_state_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame cho initial belief state
        initial_frame = ttk.LabelFrame(belief_state_frame, text="Initial Belief State")
        initial_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # Thêm expand=True
        
        # Text widget để hiển thị initial belief state
        self.belief_state_text = tk.Text(initial_frame, wrap=tk.WORD, width=45, height=15)
        self.belief_state_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn cho initial belief state
        belief_scrollbar = ttk.Scrollbar(self.belief_state_text, command=self.belief_state_text.yview)
        belief_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.belief_state_text.config(yscrollcommand=belief_scrollbar.set)
        
        # Frame cho expanded belief state
        expanded_frame = ttk.LabelFrame(belief_state_frame, text="Expanded Belief State")
        expanded_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text widget để hiển thị expanded belief state
        self.expanded_belief_text = tk.Text(expanded_frame, wrap=tk.WORD, width=45, height=18)
        self.expanded_belief_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn cho expanded belief state
        expanded_scrollbar = ttk.Scrollbar(self.expanded_belief_text, command=self.expanded_belief_text.yview)
        expanded_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.expanded_belief_text.config(yscrollcommand=expanded_scrollbar.set)
        
        # Frame hiển thị goal states (bên phải trên)
        goal_states_frame = ttk.LabelFrame(right_frame, text="Goal States")
        goal_states_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text widget để hiển thị goal states
        self.goal_states_text = tk.Text(goal_states_frame, wrap=tk.WORD, width=45, height=15)
        self.goal_states_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn
        goal_scrollbar = ttk.Scrollbar(self.goal_states_text, command=self.goal_states_text.yview)
        goal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.goal_states_text.config(yscrollcommand=goal_scrollbar.set)
        
        # Frame cho các tham số
        params_frame = ttk.LabelFrame(right_frame, text="Tham số")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Max depth
        ttk.Label(params_frame, text="Độ sâu tối đa:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_depth_var = tk.StringVar(value="30")
        ttk.Entry(params_frame, textvariable=self.max_depth_var, width=5).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame cho các nút điều khiển
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nút tìm kiếm
        self.search_button = ttk.Button(control_frame, text="Bắt đầu tìm kiếm", command=self._start_search)
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Nút reset
        self.reset_button = ttk.Button(control_frame, text="Reset", command=self._reset)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame cho kết quả
        result_frame = ttk.LabelFrame(right_frame, text="Kết quả")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, after=goal_states_frame)
        
        # Text widget để hiển thị kết quả - Tăng kích thước
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, width=40, height=15)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn
        result_scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=result_scrollbar.set)
        
        # Frame cho các nút điều hướng
        nav_frame = ttk.Frame(right_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nút điều hướng
        self.prev_button = ttk.Button(nav_frame, text="Bước trước", command=self._prev_step, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.next_button = ttk.Button(nav_frame, text="Bước tiếp", command=self._next_step, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Label hiển thị step hiện tại
        self.step_label = ttk.Label(nav_frame, text="Bước: 0/0")
        self.step_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _display_initial_state(self):
        """Hiển thị initial belief state."""
        self.belief_state_text.delete(1.0, tk.END)
        initial_belief_state = self.puzzle.get_initial_belief_state()
        self.current_belief_state = initial_belief_state
        
        # Hiển thị initial belief state với từng trạng thái riêng biệt
        self.belief_state_text.insert(tk.END, f"Initial Belief State ({len(initial_belief_state)} trạng thái):\n\n")
        for i, state in enumerate(initial_belief_state):
            self.belief_state_text.insert(tk.END, f"State {i+1}:\n")
            for row in state:
                self.belief_state_text.insert(tk.END, str(row) + "\n")
            self.belief_state_text.insert(tk.END, "\n")
        
        # Hiển thị thông tin về initial belief state
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Belief State ban đầu: {len(initial_belief_state)} trạng thái\n")
        self.result_text.insert(tk.END, "Nhấn 'Bắt đầu tìm kiếm' để tìm giải pháp.\n")
    
    def _display_goal_states(self):
        """Hiển thị goal states."""
        self.goal_states_text.delete(1.0, tk.END)
        goal_states = self.puzzle.get_goal_states()
        
        self.goal_states_text.insert(tk.END, "Goal States (có 5 trạng thái đích):\n\n")
        
        for i, state in enumerate(goal_states):
            self.goal_states_text.insert(tk.END, f"Goal State {i+1}:\n")
            for row in state:
                self.goal_states_text.insert(tk.END, str(row) + "\n")
            self.goal_states_text.insert(tk.END, "\n")
        self.step_label.config(text="Bước: 0/0")
    
    def _display_expanded_belief_state(self, expanded_belief_states):
        """Hiển thị expanded belief states."""
        if not expanded_belief_states:
            return
            
        self.expanded_belief_text.delete(1.0, tk.END)
        
        # Đếm số lượng trạng thái tổng cộng trong tất cả các belief states
        total_states = sum(len(belief_state) for belief_state in expanded_belief_states)
        self.expanded_belief_text.insert(tk.END, f"Expanded Belief States: {len(expanded_belief_states)} cặp ({total_states} trạng thái)\n\n")
        
        # Hiển thị tất cả các belief states đã mở rộng
        for i, belief_state in enumerate(expanded_belief_states):
            if i < 4:  # Giới hạn hiển thị 4 belief states đầu tiên
                self.expanded_belief_text.insert(tk.END, f"Belief State {i+1} ({len(belief_state)} trạng thái):\n")
                # Hiển thị các trạng thái trong belief state
                for j, state in enumerate(belief_state):
                    self.expanded_belief_text.insert(tk.END, f"  State {j+1}:\n")
                    for row in state:
                        self.expanded_belief_text.insert(tk.END, "  " + str(row) + "\n")
                    self.expanded_belief_text.insert(tk.END, "\n")
                self.expanded_belief_text.insert(tk.END, "\n")
            elif i == 4 and len(expanded_belief_states) > 4:
                self.expanded_belief_text.insert(tk.END, f"...\n\nVà {len(expanded_belief_states) - 4} belief states khác\n")
                break
    
    def _start_search(self):
        """Bắt đầu tìm kiếm."""
        # Lấy tham số
        try:
            max_depth = int(self.max_depth_var.get())
            if max_depth < 1:
                raise ValueError("Độ sâu tối đa phải ít nhất là 1")
        except ValueError as e:
            messagebox.showerror("Tham số không hợp lệ", str(e))
            return
        
        # Cập nhật tham số
        self.search = SensorlessSearch(self.puzzle, max_depth=max_depth, max_time=10)  # Đặt giới hạn thời gian 10 giây
        
        # Xóa expanded belief state cũ (nếu có)
        self.expanded_belief_text.delete(1.0, tk.END)
        self.expanded_belief_text.insert(tk.END, "Đang tạo expanded belief state...\n")
        
        # Hiển thị thông báo đang tìm kiếm
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Đang tìm kiếm...\n")
        self.window.update()
        
        # Vô hiệu hóa nút tìm kiếm
        self.search_button.config(state=tk.DISABLED)
        
        # Thực hiện tìm kiếm (trong một luồng riêng để không block UI)
        threading.Thread(target=self._run_search).start()
    
    def _run_search(self):
        """Thực hiện tìm kiếm trong một luồng riêng."""
        # Thực hiện tìm kiếm
        start_time = time.time()
        solution_path = self.search.search()
        end_time = time.time()
        
        # Lấy thống kê
        stats = self.search.get_statistics()
        
        # Lấy và hiển thị expanded belief state
        expanded_belief_state = self.search.get_expanded_initial_belief_state()
        self.window.after(0, lambda: self._display_expanded_belief_state(expanded_belief_state))
        
        # Hiển thị kết quả trên UI thread
        self.window.after(0, lambda: self._display_results(solution_path, stats, end_time - start_time))
    
    def _display_results(self, solution_path, stats, search_time):
        """Hiển thị kết quả tìm kiếm."""
        self.solution_path = solution_path
        
        # Xóa text hiện tại
        self.result_text.delete(1.0, tk.END)
        
        if solution_path is None:
            # Không tìm thấy đường đi
            if stats.get('time_limit_reached', False):
                self.result_text.insert(tk.END, "Tìm kiếm đã vượt quá giới hạn thời gian (10 giây)!\n\n")
                self.result_text.insert(tk.END, "Thuật toán đã dừng do vượt thời gian giới hạn.\n\n")
            else:
                self.result_text.insert(tk.END, "Không tìm thấy giải pháp!\n\n")
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
        else:
            # Tìm thấy đường đi
            self.result_text.insert(tk.END, f"Đã tìm thấy giải pháp! Số bước: {len(solution_path)}\n\n")
            
            # Hiển thị đường đi
            self.result_text.insert(tk.END, "Đường đi: \n")
            for i, action in enumerate(solution_path):
                self.result_text.insert(tk.END, f"{i+1}. {action}\n")
            
            # Reset về initial state
            self.current_belief_state = self.puzzle.get_initial_belief_state()
            self.current_step = 0
            self._display_current_state()
            
            # Enable các nút điều hướng
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.NORMAL)
        
        # Hiển thị thống kê
        self.result_text.insert(tk.END, f"\nThống kê:\n")
        self.result_text.insert(tk.END, f"- Nodes mở rộng: {stats['nodes_expanded']}\n")
        self.result_text.insert(tk.END, f"- Max frontier size: {stats['max_frontier_size']}\n")
        self.result_text.insert(tk.END, f"- Kích thước belief state mở rộng: {stats['expanded_belief_state_size']}\n")
        self.result_text.insert(tk.END, f"- Thời gian tìm kiếm: {search_time:.3f} giây\n")
        
        # Cập nhật step label
        if solution_path:
            self.step_label.config(text=f"Bước: {self.current_step}/{len(solution_path)}")
        else:
            self.step_label.config(text="Bước: 0/0")
        
        # Kích hoạt lại nút tìm kiếm
        self.search_button.config(state=tk.NORMAL)
    
    def _next_step(self):
        """Đi đến bước tiếp theo trong đường đi."""
        if self.solution_path and self.current_step < len(self.solution_path):
            # Áp dụng hành động tiếp theo
            action = self.solution_path[self.current_step]
            self.current_belief_state = self.puzzle.apply_action(self.current_belief_state, action)
            self.current_step += 1
            
            # Hiển thị trạng thái mới
            self._display_current_state()
            
            # Cập nhật trạng thái các nút
            self.prev_button.config(state=tk.NORMAL)
            if self.current_step >= len(self.solution_path):
                self.next_button.config(state=tk.DISABLED)
            
            # Cập nhật step label
            self.step_label.config(text=f"Bước: {self.current_step}/{len(self.solution_path)}")
    
    def _prev_step(self):
        """Quay lại bước trước trong đường đi."""
        if self.solution_path and self.current_step > 0:
            # Quay lại từ đầu
            self.current_belief_state = self.puzzle.get_initial_belief_state()
            
            # Áp dụng các hành động đến bước trước
            self.current_step -= 1
            for i in range(self.current_step):
                action = self.solution_path[i]
                self.current_belief_state = self.puzzle.apply_action(self.current_belief_state, action)
            
            # Hiển thị trạng thái mới
            self._display_current_state()
            
            # Cập nhật trạng thái các nút
            self.next_button.config(state=tk.NORMAL)
            if self.current_step == 0:
                self.prev_button.config(state=tk.DISABLED)
            
            # Cập nhật step label
            self.step_label.config(text=f"Bước: {self.current_step}/{len(self.solution_path)}")
    
    def _display_current_state(self):
        """Hiển thị trạng thái hiện tại."""
        self.belief_state_text.delete(1.0, tk.END)
        
        # Hiển thị current belief state với từng trạng thái riêng biệt
        self.belief_state_text.insert(tk.END, f"Current Belief State ({len(self.current_belief_state)} trạng thái):\n\n")
        for i, state in enumerate(self.current_belief_state):
            self.belief_state_text.insert(tk.END, f"State {i+1}:\n")
            for row in state:
                self.belief_state_text.insert(tk.END, str(row) + "\n")
            self.belief_state_text.insert(tk.END, "\n")
    
    def _reset(self):
        """Reset về trạng thái ban đầu."""
        # Reset các biến
        self.solution_path = None
        self.current_step = 0
        
        # Hiển thị lại initial state
        self._display_initial_state()
        
        # Xoá kết quả
        self.result_text.delete(1.0, tk.END)
        
        # Disable các nút điều hướng
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
