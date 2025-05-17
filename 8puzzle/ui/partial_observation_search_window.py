
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import copy

from models.partial_observation_puzzle import PartialObservationPuzzle
from algorithms.partial_observation_search import PartialObservationSearch

class PartialObservationSearchWindow:
    """
    Cửa sổ giao diện người dùng cho thuật toán tìm kiếm với quan sát một phần (Partial Observation Search).
    Cho phép người dùng nhập thông tin về ô đã biết trong goal state, xem các goal states,
    bắt đầu tìm kiếm, xem kết quả và điều hướng qua các bước của đường đi.
    """
    
    def __init__(self, parent):
        """
        Khởi tạo cửa sổ tìm kiếm với quan sát một phần.
        
        Args:
            parent: Widget cha (main window)
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Searching with Partial Observation")
        self.window.geometry("1200x800")
        
        # Khởi tạo các biến
        self.known_row_var = tk.IntVar(value=1)
        self.known_col_var = tk.IntVar(value=1)
        self.known_value_var = tk.IntVar(value=5)
        
        # Puzzle và search sẽ được khởi tạo sau khi người dùng nhập thông tin
        self.puzzle = None
        self.search = None
        
        # Biến để lưu trữ kết quả
        self.solution_path = None
        self.current_step = 0
        self.current_belief_state = None
        
        # Tạo giao diện
        self._create_widgets()
        
        # Cập nhật goal states ban đầu
        self._update_goal_states()
    
    def _create_widgets(self):
        """Tạo các widget trên giao diện."""
        # Frame chính
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame nhập thông tin
        input_frame = ttk.LabelFrame(main_frame, text="Thông tin ô đã biết trong Goal State")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Hàng
        ttk.Label(input_frame, text="Hàng (0-2):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Spinbox(input_frame, from_=0, to=2, textvariable=self.known_row_var, width=5).grid(
            row=0, column=1, padx=5, pady=5)
        
        # Cột
        ttk.Label(input_frame, text="Cột (0-2):").grid(row=0, column=2, padx=5, pady=5)
        ttk.Spinbox(input_frame, from_=0, to=2, textvariable=self.known_col_var, width=5).grid(
            row=0, column=3, padx=5, pady=5)
        
        # Giá trị
        ttk.Label(input_frame, text="Giá trị (0-8):").grid(row=0, column=4, padx=5, pady=5)
        ttk.Spinbox(input_frame, from_=0, to=8, textvariable=self.known_value_var, width=5).grid(
            row=0, column=5, padx=5, pady=5)
        
        # Nút cập nhật
        ttk.Button(input_frame, text="Cập nhật Goal States", command=self._update_goal_states).grid(
            row=0, column=6, padx=5, pady=5)
        
        # Chia làm 2 phần: trái và phải
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame hiển thị belief state (bên trái)
        belief_state_frame = ttk.LabelFrame(left_frame, text="Belief State")
        belief_state_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text widget để hiển thị belief state - Tăng kích thước
        self.belief_state_text = tk.Text(belief_state_frame, wrap=tk.WORD, width=45, height=30)
        self.belief_state_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn
        belief_scrollbar = ttk.Scrollbar(self.belief_state_text, command=self.belief_state_text.yview)
        belief_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.belief_state_text.config(yscrollcommand=belief_scrollbar.set)
        
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
        
        # Frame cho các tham số và điều khiển (bên phải dưới)
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame cho các tham số
        params_frame = ttk.LabelFrame(control_frame, text="Tham số")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Max depth
        ttk.Label(params_frame, text="Độ sâu tối đa:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_depth_var = tk.StringVar(value="30")
        ttk.Entry(params_frame, textvariable=self.max_depth_var, width=5).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame cho các nút điều khiển
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nút tìm kiếm
        self.search_button = ttk.Button(button_frame, text="Bắt đầu tìm kiếm", command=self._start_search)
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Nút reset
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self._reset)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame cho kết quả - Tăng kích thước và chuyển lên trên control_frame
        result_frame = ttk.LabelFrame(right_frame, text="Kết quả")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, after=goal_states_frame, before=control_frame)
        
        # Text widget để hiển thị kết quả - Tăng kích thước
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, width=40, height=15)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn
        result_scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=result_scrollbar.set)
        
        # Frame cho các nút điều hướng
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nút điều hướng
        self.prev_button = ttk.Button(nav_frame, text="Bước trước", command=self._prev_step, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.next_button = ttk.Button(nav_frame, text="Bước tiếp", command=self._next_step, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Label hiển thị bước hiện tại
        self.step_label = ttk.Label(nav_frame, text="Bước: 0/0")
        self.step_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _update_goal_states(self):
        """Cập nhật và hiển thị goal states dựa trên thông tin ô đã biết."""
        row = self.known_row_var.get()
        col = self.known_col_var.get()
        value = self.known_value_var.get()
        
        # Khởi tạo puzzle với thông tin mới
        self.puzzle = PartialObservationPuzzle((row, col), value)
        self.search = PartialObservationSearch(self.puzzle)
        
        # Hiển thị goal states
        self.goal_states_text.delete(1.0, tk.END)
        self.goal_states_text.insert(tk.END, f"Goal States (với ô ({row},{col}) có giá trị {value}):\n\n")
        
        for i, state in enumerate(self.puzzle.goal_states):
            self.goal_states_text.insert(tk.END, f"Goal State {i+1}:\n")
            for row in state:
                self.goal_states_text.insert(tk.END, str(row) + "\n")
            self.goal_states_text.insert(tk.END, "\n")
        
        # Hiển thị initial belief state
        self.belief_state_text.delete(1.0, tk.END)
        initial_belief_state = self.puzzle.get_initial_belief_state()
        self.belief_state_text.insert(tk.END, self.puzzle.belief_state_to_string(initial_belief_state))
        
        # Reset các biến
        self.solution_path = None
        self.current_step = 0
        self.current_belief_state = initial_belief_state
        
        # Reset giao diện
        self.result_text.delete(1.0, tk.END)
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.step_label.config(text="Bước: 0/0")
    
    def _start_search(self):
        """Bắt đầu tìm kiếm."""
        try:
            # Lấy tham số
            max_depth = int(self.max_depth_var.get())
            
            # Khởi tạo search với tham số mới
            self.search = PartialObservationSearch(self.puzzle, max_depth)
            
            # Disabled nút tìm kiếm trong quá trình thực hiện
            self.search_button.config(state=tk.DISABLED)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Đang tìm kiếm...\n")
            
            # Thực hiện tìm kiếm trong một luồng riêng
            thread = threading.Thread(target=self._run_search)
            thread.daemon = True
            thread.start()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập các tham số hợp lệ.")
    
    def _run_search(self):
        """Thực hiện tìm kiếm trong một luồng riêng."""
        start_time = time.time()
        solution_path = self.search.search()
        search_time = time.time() - start_time
        
        # Lấy thống kê
        stats = self.search.get_statistics()
        
        # Hiển thị kết quả trên giao diện chính
        self.window.after(0, lambda: self._display_results(solution_path, stats, search_time))
    
    def _display_results(self, solution_path, stats, search_time):
        """
        Hiển thị kết quả tìm kiếm.
        
        Args:
            solution_path: Đường đi từ initial state đến goal state
            stats: Thống kê của quá trình tìm kiếm
            search_time: Thời gian tìm kiếm (giây)
        """
        self.solution_path = solution_path
        
        # Xóa nội dung cũ
        self.result_text.delete(1.0, tk.END)
        
        if solution_path is None:
            # Không tìm thấy đường đi
            self.result_text.insert(tk.END, "Không tìm thấy đường đi trong độ sâu giới hạn.\n")
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
        """Hiển thị belief state hiện tại."""
        self.belief_state_text.delete(1.0, tk.END)
        self.belief_state_text.insert(tk.END, self.puzzle.belief_state_to_string(self.current_belief_state))
    
    def _reset(self):
        """Reset về trạng thái ban đầu."""
        # Reset các biến
        self.solution_path = None
        self.current_step = 0
        self.current_belief_state = self.puzzle.get_initial_belief_state()
        
        # Hiển thị lại initial state
        self._display_current_state()
        
        # Reset giao diện
        self.result_text.delete(1.0, tk.END)
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.step_label.config(text="Bước: 0/0")
