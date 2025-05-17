"""
Puzzle board widget implementation for 8-puzzle GUI
"""
import tkinter as tk
from tkinter import ttk

class PuzzleBoard(ttk.Frame):
    def __init__(self, parent, cell_size=80):
        super().__init__(parent)
        self.cell_size = cell_size
        self.cells = []
        self.create_board()
        
    def create_board(self):
        """Tạo giao diện bảng 3x3"""
        style = ttk.Style()
        style.configure('Puzzle.TFrame', background='white')
        style.configure('Info.TLabel', font=('Arial', 11, 'bold'), foreground='#1976d2')
        style.configure('Info.TFrame', background='#f5f5f5', relief='raised', borderwidth=1)
        
        # Frame chính cho bảng puzzle
        self.board_frame = ttk.Frame(self, style='Puzzle.TFrame', padding=10)
        self.board_frame.grid(row=0, column=0)
        
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
                row.append(cell)
            self.cells.append(row)
            
        # Sử dụng styles từ MainWindow cho thông tin của Solution Visualization
        self.info_frame = ttk.Frame(self, style='SolutionInfo.TFrame', padding=15)
        self.info_frame.grid(row=1, column=0, sticky='ew', pady=10, padx=5)
        
        # Tạo container cho các nhãn với background rõ ràng
        labels_container = ttk.Frame(self.info_frame)
        labels_container.pack(fill=tk.X, expand=True, pady=5)
        
        # Label hiển thị số bước với style mới, rõ ràng hơn
        self.steps_label = ttk.Label(labels_container, text="Steps: 00", style='SolutionInfo.TLabel')
        self.steps_label.pack(side='left', padx=25)
        
        # Label hiển thị thời gian với style mới, rõ ràng hơn
        self.time_label = ttk.Label(labels_container, text="Time: 0.00s", style='SolutionInfo.TLabel')
        self.time_label.pack(side='right', padx=25)
    
    def update_board(self, state):
        """Cập nhật hiển thị trạng thái mới"""
        for i in range(3):
            for j in range(3):
                self.cells[i][j].delete('all')
                if state[i][j] != 0:
                    # Vẽ số
                    self.cells[i][j].create_text(
                        self.cell_size//2,
                        self.cell_size//2,
                        text=str(state[i][j]),
                        font=('Arial', 24, 'bold')
                    )
                    
    def update_info(self, steps, time):
        """Cập nhật thông tin số bước và thời gian"""
        # Định dạng số bước với số 0 ở đầu để giữ độ rộng ổn định
        self.steps_label.config(text=f"Steps: {steps:02d}")
        self.time_label.config(text=f"Time: {time:.2f}s") 
