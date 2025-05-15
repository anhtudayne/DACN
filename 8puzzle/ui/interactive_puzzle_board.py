"""
Phiên bản nâng cao của Puzzle board cho phép tương tác để chọn trạng thái
"""
import tkinter as tk
from tkinter import ttk

class InteractivePuzzleBoard(ttk.Frame):
    def __init__(self, parent, title="Puzzle", cell_size=70, on_state_change=None):
        super().__init__(parent)
        self.cell_size = cell_size
        self.cells = []
        self.title = title
        self.current_state = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.on_state_change = on_state_change  # Callback khi trạng thái thay đổi
        self.selected_cell = None  # Để đánh dấu ô hiện tại
        self.create_board()
        
    def create_board(self):
        """Tạo giao diện bảng 3x3"""
        style = ttk.Style()
        style.configure('Puzzle.TFrame', background='white')
        style.configure('PuzzleTitle.TLabel', font=('Arial', 12, 'bold'), background='white')
        style.configure('Cell.Hover', background='#e1f5fe')
        style.configure('Cell.Selected', background='#bbdefb')
        
        # Tiêu đề cho bảng
        title_frame = ttk.Frame(self)
        title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(0, 5))
        
        title_label = ttk.Label(title_frame, text=self.title, style='PuzzleTitle.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Thêm hướng dẫn
        hint_label = ttk.Label(title_frame, text="Nhấp vào ô rồi gõ số (0-8)", style='Hint.TLabel', foreground='#666')
        hint_label.pack(side=tk.RIGHT)
        
        # Frame chính cho bảng puzzle
        self.board_frame = ttk.Frame(self, style='Puzzle.TFrame', padding=5)
        self.board_frame.grid(row=1, column=0)
        
        # Tạo các ô trong bảng
        for i in range(3):
            row = []
            for j in range(3):
                cell = tk.Canvas(
                    self.board_frame,
                    width=self.cell_size,
                    height=self.cell_size,
                    bg='white',
                    highlightthickness=2,
                    highlightbackground='gray'
                )
                cell.grid(row=i, column=j, padx=2, pady=2)
                
                # Thêm sự kiện cho cell
                cell.bind('<Button-1>', lambda event, r=i, c=j: self.cell_clicked(r, c))
                cell.bind('<Enter>', lambda event, r=i, c=j: self.cell_hover(r, c, True))
                cell.bind('<Leave>', lambda event, r=i, c=j: self.cell_hover(r, c, False))
                
                # Thêm nền mỏng hơn để trông như nhập trực tiếp
                cell.create_rectangle(
                    2, 2, self.cell_size-2, self.cell_size-2,
                    fill='#f5f5f5', outline='', tags='bg'
                )
                
                # Thêm cursor hiệu ứng
                cell.config(cursor="hand2")
                    
                row.append(cell)
            self.cells.append(row)
            
        # Frame chứa các nút
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=5, sticky='ew')
        
        # Nút Reset để đặt lại về trạng thái trống
        self.reset_button = ttk.Button(
            button_frame, 
            text="Xóa tất cả", 
            command=self.reset_board,
            style='Action.TButton'
        )
        self.reset_button.pack(side=tk.LEFT, padx=(0, 5), fill='x', expand=True)
    
    def update_board(self, state):
        """Cập nhật hiển thị trạng thái mới"""
        self.current_state = [row[:] for row in state]  # Deep copy
        
        for i in range(3):
            for j in range(3):
                self.cells[i][j].delete('all')
                
                # Vẽ nền ô
                self.cells[i][j].create_rectangle(
                    2, 2, self.cell_size-2, self.cell_size-2,
                    fill='#f5f5f5', outline='', tags='bg'
                )
                
                if state[i][j] != 0:
                    # Vẽ số
                    self.cells[i][j].create_text(
                        self.cell_size//2,
                        self.cell_size//2,
                        text=str(state[i][j]),
                        font=('Arial', 24, 'bold')
                    )
    
    def cell_clicked(self, row, col):
        """Xử lý sự kiện khi người dùng click vào một ô"""
        # Xóa highlight cũ (nếu có)
        if self.selected_cell:
            prev_row, prev_col = self.selected_cell
            # Xóa hiệu ứng được chọn
            self.cells[prev_row][prev_col].itemconfig('bg', fill='#f5f5f5')
            self.cells[prev_row][prev_col].config(highlightbackground='gray')
        
        # Đánh dấu ô được chọn
        self.selected_cell = (row, col)
        self.cells[row][col].config(highlightbackground='#2196f3')
        self.cells[row][col].itemconfig('bg', fill='#bbdefb')
        
        # Hiển thị con trỏ nhập văn bản
        self.cells[row][col].delete('cursor')
        self.cells[row][col].create_line(
            self.cell_size//2 - 5, self.cell_size//2 + 15,
            self.cell_size//2 + 5, self.cell_size//2 + 15,
            width=2, fill='#2196f3', tags='cursor'
        )
        
        # Đặt focus để nhập từ bàn phím
        self.master.focus_set()
        self.master.bind('<Key>', self.on_key_press)
    
    def get_state(self):
        """Trả về trạng thái hiện tại của bảng"""
        return [row[:] for row in self.current_state]  # Deep copy
        
    def reset_board(self):
        """Xóa toàn bộ bảng về trạng thái ban đầu"""
        self.current_state = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.update_board(self.current_state)
        
        if self.on_state_change:
            self.on_state_change(self.current_state)
            
    def set_state(self, state):
        """Thiết lập trạng thái mới cho bảng"""
        if len(state) != 3 or any(len(row) != 3 for row in state):
            raise ValueError("Trạng thái phải là ma trận 3x3")
        
        self.current_state = [row[:] for row in state]  # Tạo bản sao của state
        self.update_board(self.current_state)
        
        if self.on_state_change:
            self.on_state_change(self.current_state)
            
    def is_valid_puzzle(self):
        """Kiểm tra xem cấu hình puzzle có hợp lệ không"""
        # Đếm các số từ 0-8, mỗi số chỉ được xuất hiện đúng 1 lần
        counts = [0] * 9
        for i in range(3):
            for j in range(3):
                value = self.current_state[i][j]
                if 0 <= value <= 8:
                    counts[value] += 1
                else:
                    return False
        
        # Kiểm tra mỗi số xuất hiện đúng 1 lần
        for count in counts:
            if count != 1:
                return False
                
        return True
        
    def on_key_press(self, event):
        """Xử lý sự kiện khi người dùng nhấn phím"""
        if not self.selected_cell:
            return
            
        row, col = self.selected_cell
        key = event.char
        
        # Phím tắt điều hướng
        if event.keysym == 'Tab' or event.keysym == 'Return':
            self.move_to_next_cell(row, col)
            return
        elif event.keysym == 'Up' and row > 0:
            self.select_cell(row - 1, col)
            return
        elif event.keysym == 'Down' and row < 2:
            self.select_cell(row + 1, col)
            return
        elif event.keysym == 'Left' and col > 0:
            self.select_cell(row, col - 1)
            return
        elif event.keysym == 'Right' and col < 2:
            self.select_cell(row, col + 1)
            return
        elif event.keysym == 'BackSpace' or event.keysym == 'Delete':
            # Xóa giá trị hiện tại
            value = 0
        elif key.isdigit() and 0 <= int(key) <= 8:
            # Nếu là số từ 0-8
            value = int(key)
        else:
            return
            
        # Cập nhật trạng thái
        self.current_state[row][col] = value
        
        # Vẽ lại ô
        self.cells[row][col].delete('all')
        
        # Vẽ nền ô
        self.cells[row][col].create_rectangle(
            2, 2, self.cell_size-2, self.cell_size-2,
            fill='#bbdefb', outline='', tags='bg'
        )
        
        # Vẽ con trỏ
        self.cells[row][col].create_line(
            self.cell_size//2 - 5, self.cell_size//2 + 15,
            self.cell_size//2 + 5, self.cell_size//2 + 15,
            width=2, fill='#2196f3', tags='cursor'
        )
        
        if value != 0:
            self.cells[row][col].create_text(
                self.cell_size//2,
                self.cell_size//2,
                text=str(value),
                font=('Arial', 24, 'bold')
            )
        
        # Tự động di chuyển đến ô tiếp theo khi nhập số
        if key.isdigit() and 0 <= int(key) <= 8:
            self.move_to_next_cell(row, col)
            
        # Gọi callback nếu có
        if self.on_state_change:
            self.on_state_change(self.current_state)
                
    def cell_hover(self, row, col, enter):
        """Xử lý sự kiện khi chuột di chuyển vào hoặc ra khỏi ô"""
        if self.selected_cell and self.selected_cell == (row, col):
            return  # Đã được chọn, không cần hiệu ứng hover
            
        # Thay đổi màu nền khi hover
        if enter:
            self.cells[row][col].itemconfig('bg', fill='#e1f5fe')
        else:
            self.cells[row][col].itemconfig('bg', fill='#f5f5f5')
    
    def select_cell(self, row, col):
        """Chọn một ô cụ thể"""
        # Xóa highlight cũ (nếu có)
        if self.selected_cell:
            prev_row, prev_col = self.selected_cell
            # Xóa hiệu ứng được chọn
            self.cells[prev_row][prev_col].itemconfig('bg', fill='#f5f5f5')
            self.cells[prev_row][prev_col].config(highlightbackground='gray')
            self.cells[prev_row][prev_col].delete('cursor')
        
        # Đánh dấu ô được chọn
        self.selected_cell = (row, col)
        self.cells[row][col].config(highlightbackground='#2196f3')
        self.cells[row][col].itemconfig('bg', fill='#bbdefb')
        
        # Hiển thị con trỏ nhập văn bản
        self.cells[row][col].delete('cursor')
        self.cells[row][col].create_line(
            self.cell_size//2 - 5, self.cell_size//2 + 15,
            self.cell_size//2 + 5, self.cell_size//2 + 15,
            width=2, fill='#2196f3', tags='cursor'
        )
        
        # Đặt focus để nhập từ bàn phím
        self.master.focus_set()
        self.master.bind('<Key>', self.on_key_press)
        
    def move_to_next_cell(self, row, col):
        """Di chuyển đến ô tiếp theo"""
        next_col = (col + 1) % 3
        next_row = row if next_col != 0 else (row + 1) % 3
        self.select_cell(next_row, next_col)
