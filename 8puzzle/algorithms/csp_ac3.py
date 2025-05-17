"""
Thuật toán Arc Consistency #3 (AC-3) cho bài toán 8-puzzle CSP

Định nghĩa:
    Thuật toán AC-3 (Arc Consistency Algorithm #3) là một thuật toán đạt được tính nhất quán cung (arc-consistency) 
    trong các bài toán thoả mãn ràng buộc (Constraint Satisfaction Problems - CSP). Thuật toán giúp loại bỏ các 
    giá trị không thỏa mãn ràng buộc khỏi domain của các biến trước khi thực hiện backtracking.

Nguyên lý hoạt động:
    1. Khởi tạo domain cho mỗi biến (mỗi ô trong bảng 3x3 là một biến)
    2. Tạo ra hàng đợi Q chứa tất cả các cung (X_i, X_j) giữa các biến có ràng buộc
    3. Lặp lại cho đến khi hàng đợi rỗng:
       a. Lấy ra một cung (X_i, X_j) từ hàng đợi
       b. Gọi hàm REVISE(X_i, X_j) để loại bỏ các giá trị không thỏa mãn ràng buộc từ domain của X_i
       c. Nếu domain của X_i bị thay đổi, thêm các cung (X_k, X_i) vào hàng đợi
    4. Sau khi hoàn thành AC-3, tiếp tục với thuật toán backtracking truyền thống

Ưu điểm:
    1. Giảm số lần backtracking: Thu hẹp domain trước nên giảm số lần phải quay lui
    2. Phát hiện sớm các trường hợp không thể giải: Nếu domain trở thành rỗng, chứng tỏ bài toán không có lời giải
    3. Tăng hiệu quả tổng thể: Kết hợp với các kỹ thuật chọn biến thông minh như MRV (Minimum Remaining Values)

Kết hợp với Backtracking:
    Thuật toán AC-3 thường được sử dụng như bước tiền xử lý trước khi thực hiện backtracking.
    AC-3 loại bỏ các giá trị không phù hợp, sau đó thuật toán backtracking sẽ tìm lời giải trong không gian đã thu hẹp.
"""

import time
import copy
import random
from queue import Queue
from tkinter import Toplevel, Frame, Label, Button, BOTH, Text, Scrollbar, RIGHT, Y, LEFT, END
from models.puzzle import Puzzle

class CSPARC3:
    """Giải thuật toán Arc Consistency #3 (AC-3) kết hợp Backtracking cho 8-puzzle"""
    
    def __init__(self, visualization_callback=None, status_callback=None, domain_callback=None, delay=0.5):
        """
        Khởi tạo thuật toán CSP AC-3
        
        Args:
            visualization_callback: Hàm callback để hiển thị trạng thái puzzle
            status_callback: Hàm callback để cập nhật trạng thái
            domain_callback: Hàm callback để hiển thị domain
            delay: Thời gian chờ giữa các bước (giây)
        """
        self.visualization_callback = visualization_callback
        self.status_callback = status_callback
        self.domain_callback = domain_callback
        self.delay = delay
        
        # Số lần thử backtracking
        self.backtracks = 0
        # Số trạng thái đã khám phá
        self.states_explored = 0
        # Số lần cập nhật domain
        self.domain_updates = 0
        
        # Khởi tạo domain và láng giềng
        self.initialize_domains()

    def initialize_domains(self):
        """Khởi tạo domain cho mỗi biến và danh sách láng giềng"""
        # Khởi tạo domain cho mỗi biến với một số ràng buộc ban đầu
        self.domains = {}
        
        # Tạo ràng buộc ban đầu dựa trên vị trí
        # Góc trên bên trái (0,0) - thường có số lớn hơn 0
        self.domains[(0, 0)] = set([1, 2, 3, 4, 5, 6, 7, 8])
        
        # Góc trên bên phải (0,2) - thường có số lớn
        self.domains[(0, 2)] = set([2, 3, 5, 6, 8])
        
        # Góc dưới bên trái (2,0) - thường có số lớn
        self.domains[(2, 0)] = set([4, 6, 7, 8])
        
        # Góc dưới bên phải (2,2) - thường có số 0 hoặc lớn
        self.domains[(2, 2)] = set([0, 5, 6, 8])
        
        # Ô giữa (1,1) - thường có số lớn
        self.domains[(1, 1)] = set([0, 1, 2, 3, 4, 5, 7, 8])
        
        # Các ô còn lại
        self.domains[(0, 1)] = set(range(9))  # 0-8
        self.domains[(1, 0)] = set(range(9))  # 0-8
        self.domains[(1, 2)] = set(range(9))  # 0-8
        self.domains[(2, 1)] = set(range(9))  # 0-8
                
        # Tạo danh sách các vị trí láng giềng (ràng buộc)
        self.neighbors = {}
        for pos1 in self.domains:
            self.neighbors[pos1] = []
            for pos2 in self.domains:
                if pos1 != pos2:  # Tất cả các ô khác đều là láng giềng
                    self.neighbors[pos1].append(pos2)
                    
        # Hiển thị thông báo về việc khởi tạo domain
        if self.status_callback:
            self.status_callback("Khởi tạo domain với các ràng buộc ban đầu dựa trên vị trí của các ô")
        
        # Trả về domain ban đầu để hiển thị
        if self.domain_callback:
            self.domain_callback(self.domains)

    def revise(self, xi, xj):
        """
        Kiểm tra và cập nhật domain của Xi dựa trên ràng buộc với Xj
        
        Args:
            xi: Vị trí (row, col) của biến Xi
            xj: Vị trí (row, col) của biến Xj
            
        Returns:
            bool: True nếu domain của Xi bị thay đổi, False nếu không
        """
        revised = False
        
        # Tạo bản sao domain để duyệt
        xi_domain = list(self.domains[xi])
        xj_domain = list(self.domains[xj])
        
        # Nếu domain của Xj chỉ có một giá trị, các giá trị trùng trong domain Xi phải bị loại bỏ
        if len(xj_domain) == 1:
            xj_value = xj_domain[0]
            if xj_value in self.domains[xi]:
                self.domains[xi].remove(xj_value)
                revised = True
                self.domain_updates += 1
                
                # Gọi callback nếu có
                if self.status_callback:
                    self.status_callback(f"Rút gọn domain của ô {xi}: Loại bỏ giá trị {xj_value} (vì ô {xj} chỉ có giá trị {xj_value})")
                
                # Hiển thị domain nếu có callback
                if self.domain_callback:
                    self.domain_callback(self.domains)
                    time.sleep(self.delay / 2)  # Delay ngắn hơn
        
        # Kiểm tra từng giá trị trong domain của Xi
        for x in xi_domain:
            # Kiểm tra xem có bất kỳ giá trị y nào trong domain của Xj thỏa mãn ràng buộc không
            has_valid_value = False
            
            for y in xj_domain:
                # Ràng buộc: x khác y (mỗi số từ 0-8 chỉ xuất hiện một lần)
                if x != y:
                    has_valid_value = True
                    break
            
            # Nếu không có giá trị hợp lệ cho x, loại bỏ x khỏi domain của Xi
            if not has_valid_value and x in self.domains[xi]:
                self.domains[xi].remove(x)
                revised = True
                self.domain_updates += 1
                
                # Gọi callback nếu có
                if self.status_callback:
                    self.status_callback(f"Rút gọn domain của ô {xi}: Loại bỏ giá trị {x} (vi phạm ràng buộc với ô {xj})")
                
                # Hiển thị domain nếu có callback
                if self.domain_callback:
                    self.domain_callback(self.domains)
                    time.sleep(self.delay / 2)  # Delay ngắn hơn
        
        return revised

    def ac3(self):
        """
        Thuật toán AC-3 để đạt được arc consistency
        
        Returns:
            bool: True nếu arc consistency đạt được, False nếu domain của bất kỳ biến nào trở thành rỗng
        """
        if self.status_callback:
            self.status_callback("Bắt đầu thuật toán AC-3 để thu hẹp domain...")
        
        # Để theo dõi tiến trình
        iteration = 0
        removed_values = 0
        
        # Khởi tạo hàng đợi với tất cả các cung
        queue = [(xi, xj) for xi in self.domains for xj in self.neighbors[xi]]
        
        if self.status_callback:
            self.status_callback(f"Tạo hàng đợi ban đầu với {len(queue)} cung cần kiểm tra")
        
        while queue:
            iteration += 1
            (xi, xj) = queue.pop(0)  # Lấy cung đầu tiên
            
            # Đếm số giá trị trước khi thu hẹp
            before_size = len(self.domains[xi])
            
            if self.revise(xi, xj):
                # Đếm số giá trị đã bị loại bỏ
                removed = before_size - len(self.domains[xi])
                removed_values += removed
                
                # Hiển thị thông tin chi tiết
                if self.status_callback:
                    self.status_callback(f"Lặp {iteration}: Đã loại bỏ {removed} giá trị từ domain của ô {xi}")
                
                # Nếu domain của Xi bị thu hẹp thành rỗng
                if len(self.domains[xi]) == 0:
                    # Domain trống -> không có giải pháp
                    if self.status_callback:
                        self.status_callback(f"AC-3: Domain của ô {xi} trở thành rỗng, không có giải pháp!")
                    return False
                    
                # Thêm các cung liên quan vào hàng đợi
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
                        
                if self.status_callback:
                    self.status_callback(f"Thêm {len(self.neighbors[xi])-1} cung mới vào hàng đợi sau khi domain của ô {xi} thay đổi")
        
        if self.status_callback:
            domains_sizes = [len(self.domains[var]) for var in self.domains]
            avg_domain_size = sum(domains_sizes) / len(domains_sizes)
            min_domain_size = min(domains_sizes)
            if min_domain_size == 1:
                # Đã xác định chắc chắn một số ô
                determined_cells = sum(1 for size in domains_sizes if size == 1)
                self.status_callback(f"AC-3 hoàn tất sau {iteration} lặp! Đã loại bỏ {removed_values} giá trị, xác định chắc chắn {determined_cells}/9 ô.")
            else:
                self.status_callback(f"AC-3 hoàn tất sau {iteration} lặp! Đã loại bỏ {removed_values} giá trị. Kích thước domain trung bình: {avg_domain_size:.2f}")
        
        return True  # Arc consistency đạt được

    def is_valid(self, assignment):
        """
        Kiểm tra xem assignment có hợp lệ không (mỗi giá trị 0-8 chỉ xuất hiện một lần)
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
        
        Returns:
            bool: True nếu assignment hợp lệ
        """
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

    def is_complete(self, assignment):
        """
        Kiểm tra xem đã gán tất cả giá trị cho puzzle và thỏa mãn tất cả ràng buộc chưa
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
        
        Returns:
            bool: True nếu đã gán tất cả giá trị và thỏa mãn tất cả ràng buộc
        """
        # Kiểm tra xem đã gán đầy đủ 9 vị trí chưa
        if len(assignment) != 9:  # 9 ô trên bảng 3x3
            return False
        
        return True  # Nếu đã gán đủ 9 vị trí và thỏa mãn tất cả ràng buộc
    
    def select_unassigned_variable(self, assignment):
        """
        Chọn vị trí tiếp theo để gán giá trị dựa trên domain nhỏ nhất (MRV - Minimum Remaining Values)
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
            
        Returns:
            tuple: Vị trí (row, col) tiếp theo để gán hoặc None nếu không có
        """
        # Tìm các biến chưa được gán
        unassigned = []
        for row in range(3):
            for col in range(3):
                position = (row, col)
                if position not in assignment:
                    unassigned.append(position)
        
        if not unassigned:
            return None
        
        # Sắp xếp theo domain nhỏ nhất (MRV - Minimum Remaining Values)
        return min(unassigned, key=lambda var: len(self.domains[var]))
    
    def order_domain_values(self, var, assignment):
        """
        Trả về các giá trị từ domain của biến, đã được sắp xếp theo độ ràng buộc tăng dần
        
        Args:
            var: Vị trí (row, col) cần gán giá trị
            assignment: Dictionary hiện tại
            
        Returns:
            list: Danh sách các giá trị từ domain, sắp xếp theo ràng buộc
        """
        # Tạo bản sao domain và chỉ lấy các giá trị trong domain hiện tại
        values = list(self.domains[var])
        random.shuffle(values)  # Trộn ngẫu nhiên để tránh trường hợp tệ nhất
        return values
    
    def backtrack(self, assignment):
        """
        Thuật toán backtracking để tìm trạng thái thỏa mãn ràng buộc
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
            
        Returns:
            dict: Gán hoàn chỉnh thỏa mãn tất cả ràng buộc, hoặc None nếu không tìm thấy
        """
        # Tăng số trạng thái đã khám phá
        self.states_explored += 1
        
        # Hiển thị trạng thái hiện tại
        if self.visualization_callback:
            current_state = self.create_state_from_assignment(assignment)
            self.visualization_callback(current_state)
            time.sleep(self.delay)
        
        # Kiểm tra xem đã hoàn thành chưa
        if self.is_complete(assignment):
            if self.status_callback:
                self.status_callback(f"Đã tìm thấy trạng thái thỏa mãn! (Khám phá: {self.states_explored}, Quay lui: {self.backtracks})")
            return assignment
        
        # Chọn biến chưa gán tiếp theo
        var = self.select_unassigned_variable(assignment)
        
        # Duyệt qua các giá trị trong domain của biến đã chọn
        for value in self.order_domain_values(var, assignment):
            # Thử gán giá trị
            assignment[var] = value
            
            if self.status_callback:
                self.status_callback(f"Thử gán giá trị {value} cho ô {var}")
            
            # Kiểm tra xem gán có hợp lệ không
            if self.is_valid(assignment):
                if self.status_callback:
                    self.status_callback(f"Gán hợp lệ: {var} = {value}")
                
                # Tiếp tục đệ quy
                result = self.backtrack(assignment)
                if result:
                    return result
            
            # Nếu không tìm thấy giải pháp, quay lui
            if self.status_callback:
                self.status_callback(f"Quay lui: Gỡ bỏ {var} = {value}")
                
            del assignment[var]
            self.backtracks += 1
            
            # Hiển thị trạng thái sau khi quay lui nếu có callback
            if self.visualization_callback:
                current_state = self.create_state_from_assignment(assignment)
                self.visualization_callback(current_state)
                time.sleep(self.delay)
        
        return None
    
    def create_state_from_assignment(self, assignment):
        """
        Tạo trạng thái puzzle từ assignment
        
        Args:
            assignment: Dictionary với key là vị trí (row, col) và value là giá trị từ 0-8
            
        Returns:
            list: Trạng thái puzzle 2D
        """
        state = [[" " for _ in range(3)] for _ in range(3)]
        for (row, col), value in assignment.items():
            state[row][col] = value
        
        return state
    
    def create_state_from_domains(self):
        """
        Tạo trạng thái hiển thị từ domain hiện tại
        
        Returns:
            dict: Thông tin domain cho từng ô
        """
        state = {}
        for pos in self.domains:
            domain = self.domains[pos]
            if len(domain) == 1:
                # Nếu domain chỉ có một giá trị, hiển thị giá trị đó
                state[pos] = list(domain)[0]
            else:
                # Nếu domain có nhiều giá trị, hiển thị tất cả
                state[pos] = sorted(list(domain))
        
        return state
    
    def solve(self):
        """
        Giải bài toán CSP - Tìm trạng thái thỏa mãn ràng buộc sử dụng AC-3 kết hợp Backtracking
        
        Returns:
            dict: Gán hoàn chỉnh thỏa mãn tất cả ràng buộc, hoặc None nếu không tìm thấy
        """
        # Khởi tạo lại các biến theo dõi
        self.backtracks = 0
        self.states_explored = 0
        self.domain_updates = 0
        
        # Khởi tạo domain cho mỗi biến
        self.initialize_domains()
        
        # Áp dụng AC-3 trước để thu hẹp domain
        if not self.ac3():
            if self.status_callback:
                self.status_callback("AC-3: Không thể thu hẹp domain, không có giải pháp!")
            return None
        
        # Tiến hành backtracking với domain đã thu hẹp
        if self.status_callback:
            self.status_callback("AC-3 hoàn tất, bắt đầu backtracking...")
        
        assignment = {}
        result = self.backtrack(assignment)
        
        # In thống kê
        print(f"Trạng thái đã khám phá: {self.states_explored}")
        print(f"Số lần quay lui: {self.backtracks}")
        print(f"Số lần cập nhật domain: {self.domain_updates}")
        
        return result


def show_ac3_visualization():
    """Hiển thị cửa sổ trực quan hóa thuật toán AC-3"""
    # Tạo cửa sổ mới
    window = Toplevel()
    window.title("CSP AC-3 - 8 Puzzle Constraints")
    # Đặt cửa sổ ở chế độ toàn màn hình
    window.state('zoomed')
    
    # Frame chính
    main_frame = Frame(window, padx=20, pady=20)
    main_frame.pack(fill=BOTH, expand=True)
    
    # Tiêu đề giải thích CSP
    header_frame = Frame(main_frame, bg="#e0f7fa")
    header_frame.pack(pady=10, fill="x")
    
    title_label = Label(header_frame, text="CSP AC-3 - Đảm bảo tính nhất quán cung và tìm giải pháp", 
          font=("Arial", 16, "bold"), bg="#e0f7fa", fg="#00695c")
    title_label.pack(pady=10)
    
    # Giải thích về ràng buộc
    constraint_frame = Frame(header_frame, bg="#e0f7fa", relief="groove", borderwidth=1)
    constraint_frame.pack(pady=5, padx=20, fill="x")
    
    Label(constraint_frame, text="Ràng buộc: Mỗi số từ 0-8 xuất hiện đúng một lần trên bảng 3x3", 
          font=("Arial", 12), bg="#e0f7fa", fg="#00838f").pack(pady=8)
    
    # Frame hiển thị nội dung chính với 2 cột
    content_frame = Frame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=10)
    
    # Cột trái: Hiển thị trạng thái puzzle
    left_frame = Frame(content_frame, padx=10)
    left_frame.pack(side="left", fill="both", expand=True)
    
    # Tiêu đề trạng thái
    Label(left_frame, text="8-Puzzle thỏa mãn các ràng buộc:", 
          font=("Arial", 12, "bold")).pack(pady=5)
    
    # Frame chứa grid puzzle
    puzzle_frame = Frame(left_frame)
    puzzle_frame.pack(pady=10)
    
    # Tạo grid 3x3 cho puzzle
    cells = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = Label(puzzle_frame, width=5, height=2, relief="ridge", 
                        font=("Arial", 16, "bold"), borderwidth=2)
            cell.grid(row=i, column=j, padx=5, pady=5)
            row.append(cell)
        cells.append(row)
    
    # Frame thông tin
    info_frame = Frame(left_frame)
    info_frame.pack(fill="x", pady=10)
    
    # Khung hiển thị trạng thái với nền và viền
    status_frame = Frame(info_frame, relief="sunken", borderwidth=2, bg="#e8f5e9")
    status_frame.pack(fill="x", pady=8, padx=5)
    
    # Nhãn trạng thái - kích thước lớn hơn, font đẹp hơn
    status_label = Label(status_frame, text="Đang chuẩn bị...", 
                        font=("Arial", 12, "bold"), fg="#2e7d32", bg="#e8f5e9", padx=10, pady=6)
    status_label.pack(fill="x")
    
    # Cột phải: Hiển thị domain và log
    right_frame = Frame(content_frame, padx=10)
    right_frame.pack(side="right", fill="both", expand=True)
    
    # Tiêu đề domain
    Label(right_frame, text="Domain của các ô:", 
          font=("Arial", 12, "bold")).pack(pady=5)
    
    # Frame chứa domain
    domain_frame = Frame(right_frame)
    domain_frame.pack(pady=10)
    
    # Tạo grid 3x3 cho domain
    domain_cells = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = Label(domain_frame, width=10, height=3, relief="ridge", 
                        font=("Arial", 9), borderwidth=1, bg="#f5f5f5",
                        text="{0,1,2,3,4,5,6,7,8}")
            cell.grid(row=i, column=j, padx=3, pady=3)
            row.append(cell)
        domain_cells.append(row)
    
    # Frame hiển thị log
    log_frame = Frame(right_frame)
    log_frame.pack(fill="both", expand=True, pady=10)
    
    Label(log_frame, text="Quá trình Backtracking CSP:", 
          font=("Arial", 12, "bold")).pack(anchor="w")
    
    # Tạo text area với thanh cuộn cho log
    log_text = Text(log_frame, width=40, height=10, wrap="word", 
                   font=("Courier", 10), bg="#f8f8f8")
    log_text.pack(side="left", fill="both", expand=True)
    
    scrollbar = Scrollbar(log_frame)
    scrollbar.pack(side="right", fill="y")
    
    log_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=log_text.yview)
    
    # Set initial state
    log_text.insert("end", "Chưa có bước nào...\n")
    log_text.config(state="disabled")
    
    # Nút bắt đầu/dừng
    button_frame = Frame(main_frame)
    button_frame.pack(pady=15)
    
    # Cập nhật hiển thị trạng thái
    def update_visualization(state):
        """Cập nhật hiển thị trạng thái"""
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                cells[i][j].config(text=str(value))
                
                # Màu sắc khác nhau cho các giá trị
                if value == 0:
                    cells[i][j].config(bg="white", fg="black")
                elif value == " ":
                    cells[i][j].config(bg="#f5f5f5", fg="black")
                else:
                    # Màu gradient từ xanh đến cam
                    colors = ["#e3f2fd", "#bbdefb", "#90caf9", "#64b5f6", 
                             "#42a5f5", "#2196f3", "#1e88e5", "#1976d2", "#1565c0"]
                    cells[i][j].config(bg=colors[value-1] if value in range(1, 9) else "#e0e0e0", fg="black")
        
        # Cập nhật UI
        window.update()
    
    # Cập nhật hiển thị domain
    def update_domains(domains):
        """Cập nhật hiển thị domain"""
        for i in range(3):
            for j in range(3):
                pos = (i, j)
                domain = domains.get(pos, set())
                
                if len(domain) == 1:
                    # Nếu domain chỉ có một giá trị
                    value = list(domain)[0]
                    domain_cells[i][j].config(text=str(value), bg="#e8f5e9", fg="#2e7d32")
                else:
                    # Hiển thị tất cả giá trị trong domain
                    domain_text = str(sorted(list(domain))).replace('[', '{').replace(']', '}')
                    domain_cells[i][j].config(text=domain_text, 
                                           bg="#fff3e0" if len(domain) < 9 else "#f5f5f5", 
                                           fg="#e65100" if len(domain) < 5 else "#bf360c")
        
        # Cập nhật UI
        window.update()
    
    def update_status(message):
        """Cập nhật trạng thái với màu sắc phù hợp"""
        # Xác định màu sắc dựa trên loại thông báo
        if "Quay lui" in message:
            fg_color = "#e53935"  # Đỏ cho quay lui
            bg_color = "#ffebee"
            log_tag = "error"
        elif "Hợp lệ" in message or "AC-3 hoàn tất" in message:
            fg_color = "#43a047"  # Xanh lá cho hợp lệ
            bg_color = "#e8f5e9" 
            log_tag = "success"
        elif "Không hợp lệ" in message or "không có giải pháp" in message:
            fg_color = "#ff9800"  # Cam cho không hợp lệ
            bg_color = "#fff3e0"
            log_tag = "warning"
        elif "Đã tìm thấy" in message:
            fg_color = "#1e88e5"  # Xanh dương cho kết quả
            bg_color = "#e3f2fd"
            log_tag = "info"
        elif "Rút gọn domain" in message:
            fg_color = "#7b1fa2"  # Tím cho AC-3
            bg_color = "#f3e5f5"
            log_tag = "ac3"
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
        log_text.tag_config("ac3", foreground="#7b1fa2", font=("Courier", 10, "italic"))
        log_text.tag_config("normal", foreground="#616161", font=("Courier", 10))
        
        # Chèn văn bản với tag
        log_text.insert("end", message + "\n", log_tag)
        log_text.see("end")  # Cuộn xuống cuối
        log_text.config(state="disabled")
        
        # Cập nhật UI
        window.update()
    
    def start_solving():
        """Bắt đầu giải bài toán CSP với AC-3"""
        # Xóa log cũ
        log_text.config(state="normal")
        log_text.delete(1.0, "end")
        log_text.insert("end", "Bắt đầu tìm trạng thái thỏa mãn ràng buộc với AC-3...\n")
        log_text.config(state="disabled")
        
        # Cập nhật trạng thái
        status_label.config(text="Đang tìm trạng thái thỏa mãn ràng buộc với AC-3...", fg="green")
        start_button.config(state="disabled")
        
        # Tạo solver với cả visualization_callback, status_callback và domain_callback
        solver = CSPARC3(
            visualization_callback=update_visualization, 
            status_callback=update_status,
            domain_callback=update_domains,
            delay=0.5
        )
        
        # Giải CSP với AC-3
        result = solver.solve()
        
        # Hiển thị kết quả
        if result:
            final_message = f"Đã tìm thấy trạng thái thỏa mãn! (Khám phá: {solver.states_explored}, Quay lui: {solver.backtracks}, Cập nhật domain: {solver.domain_updates})"
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
