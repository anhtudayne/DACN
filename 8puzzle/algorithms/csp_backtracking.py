"""
CSP Backtracking for 8-puzzle
"""
import time
import copy
import random
from tkinter import Toplevel, Frame, Label, Button, BOTH
from models.puzzle import Puzzle

class CSPBacktracking:
    """Giải thuật toán CSP Backtracking cho 8-puzzle"""
    
    def __init__(self, visualization_callback=None, status_callback=None, delay=0.5):
        """
        Khởi tạo thuật toán CSP Backtracking
        
        Args:
            visualization_callback: Hàm callback để hiển thị trạng thái
            status_callback: Hàm callback để cập nhật trạng thái
            delay: Thời gian chờ giữa các bước (giây)
        """
        self.visualization_callback = visualization_callback
        self.status_callback = status_callback
        self.delay = delay
        # Số lần thử backtracking
        self.backtracks = 0
        # Số trạng thái đã khám phá
        self.states_explored = 0
        
    def is_complete(self, assignment):
       
        # Kiểm tra xem đã gán đầy đủ 9 vị trí chưa
        if len(assignment) != 9:  # 9 ô trên bảng 3x3
            return False
        
        
        return True  # Nếu đã gán đủ 9 vị trí và thỏa mãn tất cả ràng buộc
    
    def is_valid(self, assignment):
        
        # Lấy danh sách các giá trị trong assignment
        values = list(assignment.values())
        
        # Kiểm tra có giá trị nào xuất hiện nhiều hơn một lần không
        for value in range(9):  # 0-8
            if values.count(value) > 1:
                return False
                
        # Kiểm tra có giá trị nào nằm ngoài khoảng từ 0-8 không
        if any(v < 0 or v > 8 for v in values):
            return False
            
        return True
    
    def is_solvable(self, assignment):
       
        # Kiểm tra mỗi số từ 0-8 chỉ xuất hiện đúng một lần (ràng buộc chính)
        values = list(assignment.values())
        return len(values) == len(set(values)) and all(0 <= v <= 8 for v in values)
    
    def select_unassigned_variable(self, assignment):
       
        # Tìm các vị trí chưa được gán
        unassigned = []
        for row in range(3):
            for col in range(3):
                if (row, col) not in assignment:
                    unassigned.append((row, col))
        
        # Nếu không có, trả về None
        if not unassigned:
            return None
        
        # Chọn ngẫu nhiên một vị trí trong các vị trí chưa được gán
        import random
        return random.choice(unassigned)
    
    def order_domain_values(self, var, assignment):
       
        all_values = list(range(9))  # 0-8
        
        import random
        random.shuffle(all_values)
        
        return all_values
    
    def backtrack(self, assignment):
       
        self.states_explored += 1
        
        if self.is_complete(assignment):
            return assignment
        
        # Chọn vị trí tiếp theo để gán (ngẫu nhiên)
        var = self.select_unassigned_variable(assignment)
        
        # Thử các giá trị có thể (ngẫu nhiên)
        for value in self.order_domain_values(var, assignment):
            # Gán giá trị và kiểm tra tính hợp lệ
            assignment[var] = value
            
            # Hiển thị trạng thái hiện tại
            if self.visualization_callback:
                current_state = self.create_state_from_assignment(assignment)
                self.visualization_callback(current_state)
                time.sleep(self.delay)
            
            # Kiểm tra tính hợp lệ
            valid = self.is_valid(assignment)
            
            # Cập nhật giao diện với trạng thái hợp lệ/không hợp lệ
            if self.visualization_callback and hasattr(self, 'status_callback') and self.status_callback:
                if valid:
                    self.status_callback(f"Tại ({var[0]},{var[1]}) = {value}: Hợp lệ, tiếp tục...")
                else:
                    self.status_callback(f"Tại ({var[0]},{var[1]}) = {value}: Không hợp lệ, thử giá trị khác...")
            
            if valid:
                # Tiếp tục với biến tiếp theo (ngẫu nhiên)
                result = self.backtrack(assignment)
                if result:
                    return result
            
            # Quay lui - hiển thị có sự quay lui
            if self.visualization_callback and hasattr(self, 'status_callback') and self.status_callback:
                self.status_callback(f"Quay lui từ ({var[0]},{var[1]}) = {value}")
                
            del assignment[var]
            self.backtracks += 1
            
            # Hiển thị trạng thái sau khi quay lui
            if self.visualization_callback:
                current_state = self.create_state_from_assignment(assignment)
                self.visualization_callback(current_state)
                time.sleep(self.delay)
        
        return None
    
    def create_state_from_assignment(self, assignment):
     
        state = [[0 for _ in range(3)] for _ in range(3)]
        for (row, col), value in assignment.items():
            state[row][col] = value
        
        return state
    
    def solve(self):
        """
        Giải bài toán CSP - Tìm trạng thái thỏa mãn ràng buộc
        
        Returns:
            dict: Gán hoàn chỉnh thỏa mãn tất cả ràng buộc, hoặc None nếu không tìm thấy
        """
        # Bắt đầu với assignment rỗng
        assignment = {}
        
        # Reset thống kê
        self.backtracks = 0
        self.states_explored = 0
        
        # Thực hiện backtracking
        result = self.backtrack(assignment)
        
        # Hiển thị thống kê
        print(f"Trạng thái đã khám phá: {self.states_explored}")
        print(f"Số lần quay lui: {self.backtracks}")
        
        return result

def show_backtracking_visualization():
    """Hiển thị cửa sổ trực quan hóa thuật toán backtracking"""
    # Tạo cửa sổ mới
    window = Toplevel()
    window.title("CSP Backtracking - 8 Puzzle Constraints")
    # Đặt cửa sổ ở chế độ toàn màn hình
    window.state('zoomed')
    
    # Frame chính
    main_frame = Frame(window, padx=20, pady=20)
    main_frame.pack(fill=BOTH, expand=True)
    
    # Tiêu đề giải thích CSP
    header_frame = Frame(main_frame, bg="#e0f7fa")
    header_frame.pack(pady=10, fill="x")
    
    title_label = Label(header_frame, text="CSP Backtracking - Tìm trạng thái thỏa mãn tất cả ràng buộc", 
          font=("Arial", 16, "bold"), bg="#e0f7fa", fg="#00695c")
    title_label.pack(pady=10)
    
    # Giải thích về ràng buộc
    constraint_frame = Frame(header_frame, bg="#e0f7fa", relief="groove", borderwidth=1)
    constraint_frame.pack(pady=5, padx=20, fill="x")
    
    Label(constraint_frame, text="Ràng buộc: Mỗi số từ 0-8 xuất hiện đúng một lần trên bảng 3x3", 
          font=("Arial", 12), bg="#e0f7fa", fg="#00838f").pack(pady=8)
    
    # Frame hiển thị trạng thái hiện tại
    current_frame = Frame(main_frame)
    current_frame.pack(pady=10)
    
    Label(current_frame, text="8-Puzzle thỏa mãn các ràng buộc:", font=("Arial", 12, "bold")).pack()
    
    # Grid hiển thị trạng thái hiện tại - Tăng kích thước ô
    current_grid = Frame(current_frame)
    current_grid.pack(pady=10)
    
    current_labels = []
    for i in range(3):
        row_labels = []
        for j in range(3):
            label = Label(current_grid, text=" ", width=3, height=1, 
                         font=("Arial", 18, "bold"), relief="raised", padx=12, pady=12,
                         bg="#f0f0f0", borderwidth=2)
            label.grid(row=i, column=j, padx=3, pady=3)
            row_labels.append(label)
        current_labels.append(row_labels)
    
    # Frame cho thông tin
    info_frame = Frame(main_frame)
    info_frame.pack(pady=10, fill="x")
    
    # Thêm hộp văn bản cuộn để hiển thị các bước
    from tkinter import scrolledtext
    
    # Tiêu đề cho log
    Label(info_frame, text="Quá trình Backtracking CSP:", font=("Arial", 11, "bold")).pack(anchor="w")
    
    # Hộp văn bản cuộn - Mở rộng chiều cao và phông chữ
    log_text = scrolledtext.ScrolledText(info_frame, height=10, width=90, font=("Courier", 10))
    log_text.pack(fill="both", expand=True, pady=8)
    log_text.insert("end", "Chưa có bước nào...\n")
    log_text.config(state="disabled")
    
    # Khung hiển thị trạng thái với nền và viền
    status_frame = Frame(info_frame, relief="sunken", borderwidth=2, bg="#e8f5e9")
    status_frame.pack(fill="x", pady=8, padx=5)
    
    # Nhãn trạng thái - kích thước lớn hơn, font đẹp hơn
    status_label = Label(status_frame, text="Đang chuẩn bị...", 
                        font=("Arial", 12, "bold"), fg="#2e7d32", bg="#e8f5e9", padx=10, pady=6)
    status_label.pack(fill="x")
    
    # Nút bắt đầu/dừng
    button_frame = Frame(main_frame)
    button_frame.pack(pady=10)
    
    def update_visualization(state):
        """Cập nhật hiển thị trạng thái"""
        for i in range(3):
            for j in range(3):
                if i < len(state) and j < len(state[i]):
                    value = state[i][j]
                    text = str(value) if value != 0 else " "
                    current_labels[i][j].config(text=text)
                else:
                    current_labels[i][j].config(text=" ")
        
        # Cập nhật UI
        window.update()
    
    def update_status(message):
        """Cập nhật trạng thái với màu sắc phù hợp"""
        # Xác định màu sắc dựa trên loại thông báo
        if "Quay lui" in message:
            fg_color = "#e53935"  # Đỏ cho quay lui
            bg_color = "#ffebee"
            log_tag = "error"
        elif "Hợp lệ" in message:
            fg_color = "#43a047"  # Xanh lá cho hợp lệ
            bg_color = "#e8f5e9" 
            log_tag = "success"
        elif "Không hợp lệ" in message:
            fg_color = "#ff9800"  # Cam cho không hợp lệ
            bg_color = "#fff3e0"
            log_tag = "warning"
        elif "Đã tìm thấy" in message:
            fg_color = "#1e88e5"  # Xanh dương cho kết quả
            bg_color = "#e3f2fd"
            log_tag = "info"
        else:
            fg_color = "#616161"  # Xám cho các thông báo thông thường
            bg_color = "#f5f5f5"
            log_tag = "normal"
        
        # Cập nhật nhãn trạng thái
        status_label.config(text=message, fg=fg_color, bg=bg_color)
        status_frame.config(bg=bg_color)
        
        # Cập nhật log với màu sắc
        log_text.config(state="normal")
        
        # Tạo tags với màu sắc
        log_text.tag_config("error", foreground="#e53935", font=("Courier", 10, "bold"))
        log_text.tag_config("success", foreground="#43a047", font=("Courier", 10))
        log_text.tag_config("warning", foreground="#ff9800", font=("Courier", 10))
        log_text.tag_config("info", foreground="#1e88e5", font=("Courier", 10, "bold"))
        log_text.tag_config("normal", foreground="#616161", font=("Courier", 10))
        
        # Chèn văn bản với tag
        log_text.insert("end", message + "\n", log_tag)
        log_text.see("end")  # Cuộn xuống cuối
        log_text.config(state="disabled")
        
        # Cập nhật UI
        window.update()
    
    def start_solving():
        """Bắt đầu giải bài toán CSP"""
        # Xóa log cũ
        log_text.config(state="normal")
        log_text.delete(1.0, "end")
        log_text.insert("end", "Bắt đầu tìm trạng thái thỏa mãn ràng buộc...\n")
        log_text.config(state="disabled")
        
        # Cập nhật trạng thái
        status_label.config(text="Đang tìm trạng thái thỏa mãn ràng buộc...", fg="green")
        start_button.config(state="disabled")
        
        # Tạo solver với cả visualization_callback và status_callback
        solver = CSPBacktracking(
            visualization_callback=update_visualization, 
            status_callback=update_status, 
            delay=0.5
        )
        
        # Giải CSP
        result = solver.solve()
        
        # Hiển thị kết quả
        if result:
            final_message = f"Đã tìm thấy trạng thái thỏa mãn! (Khám phá: {solver.states_explored}, Quay lui: {solver.backtracks})"
            status_label.config(text=final_message, fg="green")
            update_status("\n" + final_message)
            
            # Hiển thị trạng thái cuối cùng
            final_state = solver.create_state_from_assignment(result)
            update_visualization(final_state)
        else:
            final_message = "Không tìm thấy trạng thái thỏa mãn!"
            status_label.config(text=final_message, fg="red")
            update_status("\n" + final_message)
        
        start_button.config(state="normal")
    
    # Nút bắt đầu - tăng kích thước và thêm hiệu ứng
    start_button = Button(button_frame, text="Tìm Trạng Thái Thỏa Mãn", command=start_solving, 
                          font=("Arial", 12, "bold"), padx=15, pady=8, 
                          bg="#4CAF50", fg="white", relief="raised", borderwidth=3)
    start_button.pack(side="left", padx=10)
    
    # Thêm hiệu ứng hover cho nút bắt đầu
    def on_enter(e):
        start_button['background'] = '#45a049'
        
    def on_leave(e):
        start_button['background'] = '#4CAF50'
        
    start_button.bind("<Enter>", on_enter)
    start_button.bind("<Leave>", on_leave)
    
    # Nút đóng - tăng kích thước
    close_button = Button(button_frame, text="Đóng", command=window.destroy, 
                         font=("Arial", 12), padx=15, pady=8,
                         bg="#f44336", fg="white", relief="raised", borderwidth=2)
    close_button.pack(side="left", padx=10)
    
    # Hiển thị trạng thái ban đầu (rỗng)
    empty_state = [[" " for _ in range(3)] for _ in range(3)]
    update_visualization(empty_state)
    
    # Đặt focus cho cửa sổ
    window.focus_force()
    
    # Ẩn thanh trạng thái ở dưới cùng
    status_bar = Label(window, text="", bd=1, relief="sunken", anchor="w")
    status_bar.pack(side="bottom", fill="x")
    
    # Ghi đè bất kỳ statusbar nào từ cửa sổ cha
    # Tạo frame ẩn phủ toàn bộ vùng dưới cùng
    bottom_frame = Frame(window, height=30, bg=window.cget("bg"))
    bottom_frame.pack(side="bottom", fill="x")
