
import time
import random
import copy
from tkinter import Toplevel, Frame, Label, Button, BOTH, scrolledtext
from models.puzzle import Puzzle

class CSPMinConflicts:
    """Thuật toán Min-Conflicts cho bài toán 8-puzzle"""
    
    def __init__(self, visualization_callback=None, status_callback=None, delay=0.3, max_iterations=1000):
       
        self.visualization_callback = visualization_callback
        self.status_callback = status_callback
        self.delay = delay
        self.max_iterations = max_iterations
        # Số lần lặp đã thực hiện
        self.iterations = 0
        # Số trạng thái đã khám phá
        self.states_explored = 0
        # Biến chứa trạng thái hiện tại
        self.current_assignment = {}
        
    def is_complete(self, assignment):
        """
        Kiểm tra xem phân công đã hoàn thành, thỏa mãn tất cả ràng buộc chưa
        
        Ràng buộc của bài toán 8-puzzle CSP:
        - Mỗi giá trị từ 0-8 phải xuất hiện đúng một lần trên bảng 3x3
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
            
        Returns:
            bool: True nếu phân công đã hoàn thành và thỏa mãn tất cả ràng buộc
        """
        # Kiểm tra xem đã gán đầy đủ 9 vị trí chưa
        if len(assignment) != 9:  # 9 ô trên bảng 3x3
            return False
        
        # Đếm số lần xuất hiện của mỗi giá trị
        value_counts = {}
        for value in assignment.values():
            if value in value_counts:
                value_counts[value] += 1
            else:
                value_counts[value] = 1
        
        # Kiểm tra xem mỗi giá trị từ 0-8 có xuất hiện đúng một lần không
        for value in range(9):  # 0-8
            if value_counts.get(value, 0) != 1:  # Mỗi giá trị phải xuất hiện đúng một lần
                return False
        
        return True
    
    def count_conflicts(self, assignment):
        """
        Đếm số lượng xung đột trong phân công hiện tại
        
        Xung đột xảy ra khi:
        1. Một giá trị xuất hiện nhiều hơn 1 lần -> mỗi lần xuất hiện thừa tính là 1 xung đột
        2. Một giá trị không xuất hiện lần nào -> tính là 1 xung đột
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
            
        Returns:
            int: Tổng số xung đột
        """
        # Đếm số lần xuất hiện của mỗi giá trị
        value_counts = {}
        for value in assignment.values():
            if value in value_counts:
                value_counts[value] += 1
            else:
                value_counts[value] = 1
        
        conflicts = 0
        # Xử lý giá trị xuất hiện nhiều lần hoặc không xuất hiện
        for value in range(9):
            count = value_counts.get(value, 0)
            if count > 1:  # Trường hợp 1: Xuất hiện nhiều hơn 1 lần
                conflicts += (count - 1)  # Mỗi lần xuất hiện thừa là 1 xung đột
            elif count == 0:  # Trường hợp 2: Không xuất hiện
                conflicts += 1  # Tính là 1 xung đột
        
        return conflicts
    
    def is_variable_conflicting(self, var, assignment):
        """
        Kiểm tra xem một biến có đang xung đột không
        
        Args:
            var: Biến cần kiểm tra
            assignment: Phân công hiện tại
            
        Returns:
            bool: True nếu biến đang xung đột, False nếu không
        """
        if var not in assignment:
            return False
        
        value = assignment[var]
        
        # Kiểm tra xem giá trị có xuất hiện ở biến khác không
        for other_var, other_value in assignment.items():
            if other_var != var and other_value == value:
                return True
        
        return False
    
    def conflicting_variables(self, assignment):
        """
        Tìm tất cả các biến đang xung đột
        
        Args:
            assignment: Phân công hiện tại
            
        Returns:
            list: Danh sách các biến đang xung đột
        """
        conflicting = []
        
        for var in assignment:
            if self.is_variable_conflicting(var, assignment):
                conflicting.append(var)
        
        return conflicting
    
    def min_conflicts_value(self, var, assignment):
        """
        Tìm giá trị gây ra ít xung đột nhất cho biến var
        
        Args:
            var: Biến cần gán giá trị
            assignment: Phân công hiện tại
            
        Returns:
            int: Giá trị gây ra ít xung đột nhất
        """
        # Tạo phân công tạm thời
        temp_assignment = assignment.copy()
        
        # Lưu giá trị hiện tại
        current_value = assignment[var]
        
        min_conflicts = float('inf')
        min_values = []
        
        for value in range(9):  # Thử tất cả các giá trị từ 0-8
            if value == current_value:
                continue  # Bỏ qua giá trị hiện tại
                
            # Gán giá trị thử nghiệm
            temp_assignment[var] = value
            
            # Đếm số xung đột
            conflict_count = self.count_conflicts(temp_assignment)
            
            # Cập nhật giá trị tốt nhất
            if conflict_count < min_conflicts:
                min_conflicts = conflict_count
                min_values = [value]
            elif conflict_count == min_conflicts:
                min_values.append(value)
        
        # Khôi phục giá trị ban đầu
        temp_assignment[var] = current_value
        
        # Nếu không có giá trị nào tốt hơn, giữ nguyên giá trị hiện tại
        if not min_values:
            return current_value
        
        # Chọn ngẫu nhiên từ các giá trị tốt nhất
        return random.choice(min_values)
    
    def solve(self):
        """Giải bài toán 8-puzzle bằng thuật toán Min-Conflicts. Trả về phân công nếu tìm thấy trạng thái thỏa mãn, None nếu không."""
        # Khởi tạo phân công ngẫu nhiên có xung đột
        self.current_assignment = self.random_assignment()
        
        # Gửi thông báo đang bắt đầu
        if self.status_callback:
            self.status_callback("--- Bắt đầu thuật toán Min-Conflicts ---")
            self.status_callback(f"Tối đa {self.max_iterations} lần lặp trước khi dừng.")
        
        # Cập nhật visualization ban đầu
        if self.visualization_callback:
            state = self.create_state_from_assignment(self.current_assignment)
            self.visualization_callback(state)
        
        # Cập nhật số xung đột ban đầu
        conflicts = self.count_conflicts(self.current_assignment)
        if self.status_callback:
            self.status_callback(f"Trạng thái ban đầu - Số xung đột: {conflicts}")
            if conflicts == 0:  # Trường hợp khởi tạo may mắn đã thỏa mãn
                self.status_callback("(Trạng thái khởi tạo đã thỏa mãn tất cả ràng buộc - thử tạo lại với xung đột...)")
                # Thử lại khởi tạo để có xung đột
                for _ in range(5):  # Thử tối đa 5 lần
                    self.current_assignment = self.random_assignment()
                    conflicts = self.count_conflicts(self.current_assignment)
                    if conflicts > 0:
                        if self.status_callback:
                            self.status_callback(f"Trạng thái ban đầu mới - Số xung đột: {conflicts}")
                        if self.visualization_callback:
                            state = self.create_state_from_assignment(self.current_assignment)
                            self.visualization_callback(state)
                        break
        
        # Bắt đầu vòng lặp chính
        self.iterations = 0
        while self.iterations < self.max_iterations:
            self.iterations += 1
            self.states_explored += 1
            
            # Kiểm tra nếu đã thỏa mãn tất cả ràng buộc
            if self.is_complete(self.current_assignment):
                if self.status_callback:
                    self.status_callback(f"✅ Đã tìm thấy trạng thái thỏa mãn sau {self.iterations} lần lặp!")
                return self.current_assignment
            
            # Tìm các biến đang xung đột
            conflicting = self.conflicting_variables(self.current_assignment)
            if not conflicting:
                # Nếu không còn biến xung đột, nhưng is_complete vẫn False,
                # có thể có giá trị bị thiếu hoặc lỗi logic
                if self.status_callback:
                    self.status_callback("⚠️ Không còn biến xung đột, nhưng chưa đạt trạng thái hoàn chỉnh!")
                break
            
            # Hiển thị thông tin các biến đang xung đột (cho bước đầu tiên hoặc mỗi 10 bước)
            if self.iterations == 1 or self.iterations % 10 == 0:
                if self.status_callback:
                    conflict_vars = [f"{var}={self.current_assignment[var]}" for var in conflicting]
                    self.status_callback(f"Các ô đang xung đột: {', '.join(conflict_vars)}")
            
            # Chọn ngẫu nhiên một biến đang xung đột
            var = random.choice(conflicting)
            
            # Tìm giá trị tốt nhất cho biến đó
            value = self.min_conflicts_value(var, self.current_assignment)
            
            # Gán giá trị mới
            old_value = self.current_assignment[var]
            self.current_assignment[var] = value
            
            # Cập nhật số xung đột
            conflicts = self.count_conflicts(self.current_assignment)
            
            # Gửi thông báo
            if self.status_callback:
                message = f"Lặp #{self.iterations}: Đổi ô {var} từ {old_value} → {value}. Xung đột còn lại: {conflicts}"
                self.status_callback(message)
            
            # Cập nhật visualization
            if self.visualization_callback:
                state = self.create_state_from_assignment(self.current_assignment)
                self.visualization_callback(state)
            
            # Chờ một chút để hiển thị quá trình
            time.sleep(self.delay)
        
        # Nếu vượt quá số lần lặp tối đa
        if self.status_callback:
            self.status_callback(f"❌ Không tìm thấy trạng thái thỏa mãn sau {self.max_iterations} lần lặp!")
            
        return None
    
    def random_assignment(self):
        """
        Tạo một phân công ngẫu nhiên cho 8-puzzle, cố ý tạo các xung đột
        
        Returns:
            dict: Phân công ngẫu nhiên có xung đột
        """
        assignment = {}
        
        # Phương pháp 1: Tạo ngẫu nhiên có xung đột
        # Lấy các giá trị từ 0-8, nhưng lặp lại một số giá trị để tạo xung đột
        # và bỏ qua một số giá trị khác
        values = []  # Danh sách giá trị sẽ gán cho các ô
        
        # Chọn 3 giá trị ngẫu nhiên để lặp lại, mỗi giá trị lặp lại 2 lần
        duplicated_values = random.sample(range(9), 3)
        for value in duplicated_values:
            values.extend([value, value])  # Thêm mỗi giá trị 2 lần
        
        # Thêm các giá trị không trùng lặp khác để đầy đủ 9 giá trị
        remaining_values = [v for v in range(9) if v not in duplicated_values]
        # Chọn tiếp 3 giá trị từ những giá trị còn lại
        remaining_choices = random.sample(remaining_values, 3)
        values.extend(remaining_choices)
        
        # Đảo ngẫu nhiên thứ tự các giá trị
        random.shuffle(values)
        
        # Gán các giá trị vào assignment
        index = 0
        for row in range(3):
            for col in range(3):
                if index < len(values):
                    assignment[(row, col)] = values[index]
                    index += 1
                else:
                    # Nếu hết giá trị, gán giá trị ngẫu nhiên
                    assignment[(row, col)] = random.choice(range(9))
        
        return assignment
    
    def create_state_from_assignment(self, assignment):
        """
        Tạo trạng thái puzzle từ assignment
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
            
        Returns:
            list: Trạng thái puzzle 2D
        """
        state = [[0 for _ in range(3)] for _ in range(3)]
        
        for (row, col), value in assignment.items():
            state[row][col] = value
            
        return state

def show_min_conflicts_visualization():
    """Hiển thị cửa sổ trực quan hóa thuật toán Min-Conflicts"""
    # Tạo cửa sổ mới
    window = Toplevel()
    window.title("Min-Conflicts - 8 Puzzle CSP")
    
    # Cấu hình cửa sổ toàn màn hình
    window.state('zoomed')  # Toàn màn hình cho Windows
    
    # Đặt kích thước tối thiểu để đảm bảo tính ổn định
    window.minsize(800, 600)
    
    # Đặt focus cho cửa sổ mới
    window.focus_set()
    
    # Frame chính
    main_frame = Frame(window, padx=20, pady=20)
    main_frame.pack(fill=BOTH, expand=True)
    
    # Tiêu đề và mô tả
    title_frame = Frame(main_frame, bg="#e1f5fe")
    title_frame.pack(pady=10, fill="x")
    
    Label(title_frame, text="Thuật toán Min-Conflicts - CSP", 
          font=("Arial", 16, "bold"), bg="#e1f5fe", fg="#0277bd").pack(pady=5)
    
    Label(title_frame, 
          text="Tìm trạng thái thỏa mãn ràng buộc: mỗi số từ 0-8 xuất hiện đúng một lần", 
          font=("Arial", 11), bg="#e1f5fe", fg="#01579b").pack(pady=5)
    
    # Frame hiển thị puzzle
    puzzle_frame = Frame(main_frame)
    puzzle_frame.pack(pady=15)
    
    Label(puzzle_frame, text="Trạng thái hiện tại:", 
          font=("Arial", 12, "bold")).pack(pady=5)
    
    # Grid hiển thị puzzle - tăng kích thước cho màn hình lớn
    puzzle_grid = Frame(puzzle_frame)
    puzzle_grid.pack(pady=15)
    
    cell_labels = []
    for i in range(3):
        row_labels = []
        for j in range(3):
            # Tạo frame cho mỗi ô để dễ tùy chỉnh
            cell_frame = Frame(puzzle_grid, borderwidth=2, relief="raised", 
                              width=75, height=75, bg="#f5f5f5")
            cell_frame.grid(row=i, column=j, padx=4, pady=4)
            cell_frame.pack_propagate(False)  # Giữ kích thước cố định
            
            # Label hiển thị giá trị
            label = Label(cell_frame, text=" ", 
                         font=("Arial", 18, "bold"), bg="#f5f5f5")
            label.pack(expand=True)
            
            row_labels.append(label)
        cell_labels.append(row_labels)
    
    # Frame hiển thị số xung đột
    conflict_frame = Frame(main_frame, bg="#f9fbe7")
    conflict_frame.pack(pady=10, fill="x")
    
    # Label hiển thị số xung đột
    conflict_label = Label(conflict_frame, text="Số xung đột: 0", 
                          font=("Arial", 12), bg="#f9fbe7", pady=5)
    conflict_label.pack()
    
    # Frame hiển thị log
    log_frame = Frame(main_frame)
    log_frame.pack(pady=10, fill="both", expand=True)
    
    Label(log_frame, text="Quá trình thực hiện:", 
          font=("Arial", 11, "bold")).pack(anchor="w")
    
    # Tạo text area hiển thị log
    log_text = scrolledtext.ScrolledText(log_frame, height=10, 
                                      font=("Courier", 10))
    log_text.pack(fill="both", expand=True, pady=5)
    log_text.insert("end", "Chưa có hoạt động nào. Nhấn nút 'Bắt đầu' để chạy thuật toán.\n")
    log_text.config(state="disabled")
    
    # Frame cho nút điều khiển
    button_frame = Frame(main_frame)
    button_frame.pack(pady=15)
    
    def update_visualization(state):
        """Cập nhật hiển thị trạng thái puzzle"""
        # Cập nhật giá trị và màu sắc cho mỗi ô
        value_counts = {}
        
        # Đếm số lần xuất hiện của mỗi giá trị
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                if value in value_counts:
                    value_counts[value] += 1
                else:
                    value_counts[value] = 1
        
        # Cập nhật hiển thị
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                text = str(value) if value != 0 else " "
                
                # Kiểm tra xung đột - nếu giá trị xuất hiện nhiều hơn 1 lần
                is_conflict = value_counts.get(value, 0) > 1
                
                # Cập nhật text và màu sắc
                cell_labels[i][j].config(
                    text=text,
                    fg="red" if is_conflict else "black",
                    bg="#ffebee" if is_conflict else "#f5f5f5"
                )
        
        # Đếm tổng số xung đột
        total_conflicts = sum(max(0, count - 1) for count in value_counts.values())
        # Thêm số giá trị thiếu hẳn
        missing_values = sum(1 for v in range(9) if v not in value_counts)
        total_conflicts += missing_values
        
        # Cập nhật label với thông tin xung đột chi tiết
        if total_conflicts == 0:
            conflict_label.config(text=f"Số xung đột: {total_conflicts} ✓", fg="green")
            conflict_frame.config(bg="#e8f5e9")  # Nền xanh nhạt
        else:
            conflict_label.config(text=f"Số xung đột: {total_conflicts}", fg="red")
            conflict_frame.config(bg="#ffebee")  # Nền đỏ nhạt
        
        # Cập nhật giao diện
        window.update()
    
    def update_log(message):
        """Cập nhật log với thông điệp mới"""
        log_text.config(state="normal")
        log_text.insert("end", message + "\n")
        log_text.see("end")  # Cuộn xuống cuối
        log_text.config(state="disabled")
        window.update()
    
    def start_solving():
        """Bắt đầu chạy thuật toán Min-Conflicts"""
        # Xóa log cũ
        log_text.config(state="normal")
        log_text.delete(1.0, "end")
        log_text.config(state="disabled")
        
        update_log("🔍 Đang khởi tạo thuật toán Min-Conflicts...")
        
        # Hiển thị hướng dẫn sử dụng thuật toán
        update_log("Thuật toán Min-Conflicts tìm kiếm trạng thái thỏa mãn ràng buộc:")  
        update_log("- Mỗi giá trị từ 0-8 phải xuất hiện đúng một lần")
        update_log("- Bắt đầu từ trạng thái có xung đột, sau đó điều chỉnh dần")
        update_log("- Mỗi bước, chọn ngẫu nhiên một ô xung đột và thay đổi giá trị")
        update_log("để giảm tổng số xung đột")
        update_log("-----------------------------------------------------")
        
        # Vô hiệu hóa nút bắt đầu
        start_button.config(state="disabled")
        
        # Cấu hình số lần lặp tối đa và độ trễ
        max_iterations = 100  # Giảm số lần lặp để quá trình không quá dài
        delay = 1.0  # Tăng thời gian chờ giữa các bước lên 3 giây để dễ theo dõi
        
        # Khởi tạo solver với max_iterations được cấu hình
        solver = CSPMinConflicts(
            visualization_callback=update_visualization,
            status_callback=update_log,
            delay=delay,
            max_iterations=max_iterations
        )
        
        # Giải bài toán
        result = solver.solve()
        
        # Hiển thị kết quả
        if result:
            final_state = solver.create_state_from_assignment(result)
            update_visualization(final_state)
            update_log(f"Đã tìm thấy trạng thái thỏa mãn sau {solver.iterations} lần lặp!")
        else:
            update_log("Không tìm thấy trạng thái thỏa mãn!")
        
        # Kích hoạt lại nút bắt đầu
        start_button.config(state="normal")
    
    # Nút bắt đầu
    start_button = Button(button_frame, text="Bắt đầu Min-Conflicts", 
                         command=start_solving,
                         font=("Arial", 12, "bold"), 
                         bg="#4CAF50", fg="white",
                         relief="raised", borderwidth=2,
                         padx=15, pady=8)
    start_button.pack(side="left", padx=10)
    
    # Hiệu ứng hover cho nút bắt đầu
    def on_enter(e):
        start_button['background'] = '#45a049'
        start_button['relief'] = 'sunken'
        
    def on_leave(e):
        start_button['background'] = '#4CAF50'
        start_button['relief'] = 'raised'
        
    start_button.bind("<Enter>", on_enter)
    start_button.bind("<Leave>", on_leave)
    
    # Nút đóng
    close_button = Button(button_frame, text="Đóng", 
                         command=window.destroy,
                         font=("Arial", 11), 
                         bg="#f44336", fg="white",
                         relief="raised", borderwidth=2,
                         padx=15, pady=8)
    close_button.pack(side="left", padx=10)
    
    # Hiển thị trạng thái ban đầu (trống)
    empty_state = [[" " for _ in range(3)] for _ in range(3)]
    update_visualization(empty_state)
    
    # Cập nhật UI
    window.mainloop()
