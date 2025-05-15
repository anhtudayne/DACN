"""
Cửa sổ tìm kiếm AND-OR Search cho bài toán 8-puzzle
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import copy
from models.and_or_puzzle import AndOrPuzzle
from algorithms.and_or_search import and_or_graph_search, format_conditional_plan, find_path_to_goal

class AndOrSearchWindow(tk.Toplevel):
    def __init__(self, parent=None):
        """Khởi tạo cửa sổ AND-OR Search"""
        super().__init__(parent)
        self.title("AND-OR Search - 8-puzzle")
        self.geometry("800x700")
        self.resizable(True, True)
        
        # Tạo Puzzle
        self.puzzle = AndOrPuzzle()
        
        # Sử dụng trạng thái đầu và đích phức tạp hơn, phù hợp cho AND-OR Search
        self.initial_state = [
            [1, 2, 3],
            [4, 0, 5],
            [7, 8, 6]
        ]
        
        self.goal_state = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        
        # Cập nhật puzzle với trạng thái cố định
        self.puzzle.initial_state = self.initial_state
        self.puzzle.goal_state = self.goal_state
        
        # Biến theo dõi trạng thái và kế hoạch
        self.solution_states = []
        self.current_state_idx = 0
        self.plan = None
        self.path = None
        self.auto_update_job = None
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        """Tạo giao diện người dùng"""
        # Frame chính
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Khu vực thông tin trạng thái
        state_frame = ttk.LabelFrame(main_frame, text="Puzzle States")
        state_frame.pack(fill=tk.X, pady=5)
        
        # Hiển thị trạng thái ban đầu và đích
        initial_text = f"Initial State: {[item for row in self.initial_state for item in row]}"
        goal_text = f"Goal State: {[item for row in self.goal_state for item in row]}"
        
        ttk.Label(state_frame, text=initial_text, font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(state_frame, text=goal_text, font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Khu vực tham số thuật toán
        params_frame = ttk.LabelFrame(main_frame, text="Algorithm Parameters")
        params_frame.pack(fill=tk.X, pady=5)
        
        # Tham số thuật toán
        self.success_prob_var = tk.StringVar(value="90")  # Tăng xác suất thành công lên 90%
        self.max_depth_var = tk.StringVar(value="30")  # Tăng độ sâu mặc định lên 30
        
        # Hiển thị xác suất thành công
        self.success_prob_label = ttk.Label(params_frame, text=f"Success probability: {self.success_prob_var.get()}%", 
                 font=("Arial", 10))
        self.success_prob_label.pack(anchor=tk.W, padx=10, pady=5)
        
        self.unsuccess_prob_label = ttk.Label(params_frame, text=f"Unsuccess probability: {100-int(self.success_prob_var.get())}%", 
                 font=("Arial", 10))
        self.unsuccess_prob_label.pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(params_frame, text=f"Max depth: {self.max_depth_var.get()}", 
                 font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Nút Run AND-OR Search
        self.run_button = ttk.Button(main_frame, text="Run AND-OR Search", command=self.run_search)
        self.run_button.pack(pady=10)
        
        # Khu vực hiển thị đường đi
        viz_frame = ttk.LabelFrame(main_frame, text="Solution Path")
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas hiển thị puzzle
        self.solution_canvas = tk.Canvas(viz_frame, width=180, height=180, bg="white")
        self.solution_canvas.pack(pady=10)
        
        # Nhãn hiển thị bước
        self.path_label = ttk.Label(viz_frame, text="Step: 0/0", font=("Arial", 10, "bold"))
        self.path_label.pack(pady=5)
        
        # Khu vực hiển thị kế hoạch có điều kiện
        result_frame = ttk.LabelFrame(main_frame, text="Conditional Plan")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text hiển thị kế hoạch
        self.solution_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=10)
        self.solution_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Vẽ trạng thái ban đầu
        self.draw_puzzle(self.initial_state)
    
    def run_search(self):
        """Thực hiện thuật toán AND-OR Search"""
        # Vô hiệu hóa nút tìm kiếm
        self.run_button.config(state=tk.DISABLED, text="Đang tìm kiếm...")
        self.update()
        
        # Reset hiển thị
        self.solution_text.delete(1.0, tk.END)
        self.solution_text.insert(tk.END, "Bắt đầu tìm kiếm kế hoạch có điều kiện...\n\n")
        self.path_label.config(text="Đang tìm kiếm...")
        
        # Chạy thuật toán trong thread riêng để không đóng băng giao diện
        threading.Thread(target=self._execute_search, daemon=True).start()
    
    def _execute_search(self):
        """Thực hiện thuật toán AND-OR Search trong thread riêng"""
        try:
            # Lấy các tham số
            success_prob = float(self.success_prob_var.get()) / 100
            max_depth = int(self.max_depth_var.get())
            max_nodes = 10000  # Tăng giới hạn số nút để có thể tìm được kế hoạch
            
            # In thông tin debug
            print(f"Thực hiện AND-OR Search với max_depth={max_depth}, max_nodes={max_nodes}, success_prob={success_prob}")
            print(f"Trạng thái đầu: {self.initial_state}")
            print(f"Trạng thái đích: {self.goal_state}")
            
            # Bắt đầu đo thời gian
            start_time = time.time()
            
            # Thực hiện tìm kiếm AND-OR
            plan = and_or_graph_search(
                self.puzzle,
                max_depth=max_depth,
                max_nodes=max_nodes,
                success_prob=success_prob
            )
            
            # Tính thời gian thực hiện
            elapsed_time = time.time() - start_time
            print(f"Kết quả tìm kiếm: {plan is not None}, thời gian: {elapsed_time:.2f}s")
            
            # Cập nhật giao diện trên main thread
            self.after(0, lambda: self._update_results(plan, elapsed_time))
        except Exception as e:
            # Xử lý ngoại lệ
            print(f"Lỗi khi tìm kiếm: {str(e)}")
            self.after(0, lambda: self._show_error(str(e)))
    
    def _update_results(self, plan, elapsed_time):
        """Hiển thị kết quả tìm kiếm"""
        # Cập nhật kế hoạch tìm thấy
        self.plan = plan
        
        # Xóa và cập nhật văn bản kết quả
        self.solution_text.delete(1.0, tk.END)
        
        if plan:
            # Tìm thấy kế hoạch
            self.solution_text.insert(tk.END, f"Tìm thấy kế hoạch có điều kiện! (thời gian: {elapsed_time:.2f}s)\n\n")
            self.solution_text.insert(tk.END, format_conditional_plan(plan, self.puzzle))
            
            # Tìm đường đi mẫu để hiển thị
            self.path = find_path_to_goal(plan, self.puzzle)
            if self.path:
                self.solution_states = self.path
                self.current_state_idx = 0
                self.update_solution_display()
                
                # Bắt đầu hiển thị tự động
                self.start_auto_visualization()
            else:
                self.path_label.config(text="Không thể hiển thị đường đi")
        else:
            # Không tìm thấy kế hoạch
            self.solution_text.insert(tk.END, f"Không tìm thấy kế hoạch! (thời gian: {elapsed_time:.2f}s)\n\n")
            self.solution_text.insert(tk.END, "Nguyên nhân có thể:\n")
            self.solution_text.insert(tk.END, "- Độ sâu tối đa không đủ\n")
            self.solution_text.insert(tk.END, "- Số nút tối đa bị hạn chế\n")
            self.solution_text.insert(tk.END, "- Không tồn tại kế hoạch có điều kiện thỏa mãn")
            
            # Cập nhật path_label để không còn hiện "Đang tìm kiếm..."
            self.path_label.config(text="Không tìm thấy kế hoạch")
        
        # Kích hoạt lại nút Run (luôn thực hiện bất kể tìm thấy kế hoạch hay không)
        self.run_button.config(state=tk.NORMAL, text="Run AND-OR Search")
    
    def _show_error(self, error_message):
        """Hiển thị thông báo lỗi"""
        # Hiển thị lỗi trong văn bản kết quả
        self.solution_text.delete(1.0, tk.END)
        self.solution_text.insert(tk.END, f"Lỗi khi thực hiện tìm kiếm: {error_message}")
        
        # Hiển thị hộp thoại lỗi
        messagebox.showerror("Lỗi", f"Lỗi khi thực hiện tìm kiếm: {error_message}")
        
        # Kích hoạt lại nút Run
        self.run_button.config(state=tk.NORMAL, text="Run AND-OR Search")
    
    def update_solution_display(self):
        """Cập nhật hiển thị giải pháp"""
        if not self.solution_states or self.current_state_idx < 0 or self.current_state_idx >= len(self.solution_states):
            return
        
        # Lấy trạng thái hiện tại
        current_state = self.solution_states[self.current_state_idx]
        
        # Vẽ puzzle
        self.draw_puzzle(current_state)
        
        # Cập nhật nhãn bước
        self.path_label.config(text=f"Step: {self.current_state_idx}/{len(self.solution_states)-1}")
    
    def start_auto_visualization(self):
        """Bắt đầu tự động hiển thị từng bước"""
        # Hủy tất cả các job auto update trước đó (nếu có)
        if self.auto_update_job:
            self.after_cancel(self.auto_update_job)
        
        # Đặt lịch cho cập nhật tiếp theo
        self.auto_update_job = self.after(500, self.auto_advance)
    
    def auto_advance(self):
        """Tự động tiến đến bước tiếp theo"""
        if not self.solution_states:
            return
        
        # Tăng chỉ số trạng thái
        self.current_state_idx = (self.current_state_idx + 1) % len(self.solution_states)
        
        # Cập nhật hiển thị
        self.update_solution_display()
        
        # Đặt lịch cho cập nhật tiếp theo
        self.auto_update_job = self.after(500, self.auto_advance)
    
    def draw_puzzle(self, state):
        """Vẽ puzzle trên canvas"""
        # Xóa canvas
        self.solution_canvas.delete("all")
        
        # Kích thước ô và biên
        cell_size = 50
        margin = 10
        
        # Vẽ các ô
        for i in range(3):
            for j in range(3):
                # Tọa độ
                x1 = margin + j * cell_size
                y1 = margin + i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Lấy giá trị
                value = state[i][j]
                
                # Vẽ ô
                self.solution_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="black",
                    width=2
                )
                
                # Vẽ số (nếu không phải ô trống)
                if value != 0:
                    self.solution_canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=str(value),
                        font=("Arial", 14, "bold")
                    )