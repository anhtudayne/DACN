"""
Main window implementation for 8-puzzle GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import os
import threading
from datetime import datetime
from ui.puzzle_board import PuzzleBoard
from ui.interactive_puzzle_board import InteractivePuzzleBoard
from models.puzzle import Puzzle
# AND-OR Search được import trực tiếp trong phương thức show_and_or_search
from algorithms.bfs import bfs_search
from algorithms.dfs import dfs_search
from algorithms.ids import ids_search
from algorithms.ucs import ucs_search
from algorithms.greedy import greedy_search
from algorithms.astar import astar_search
from algorithms.ida import ida_star_search
from algorithms.simple_hill_climbing import simple_hill_climbing
from algorithms.steepest_hill_climbing import steepest_hill_climbing
from algorithms.beam_search import beam_search
from algorithms.simulated_annealing import simulated_annealing
from algorithms.stochastic_hill_climbing import stochastic_hill_climbing
from algorithms.genetic_algorithm import genetic_algorithm
from algorithms.csp_backtracking import show_backtracking_visualization
from algorithms.q_learning import QLearning, show_qlearning_visualization

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver")
        self.root.resizable(True, True)  # Cho phép thay đổi kích thước cửa sổ
        self.root.state('zoomed')  # Mở rộng cửa sổ thành toàn màn hình (Windows)
        self.root.configure(bg='#e8f4f8')  # Màu nền chính
        
        # Thiết lập kích thước tối thiểu cho cửa sổ
        self.root.minsize(1200, 700)
        
        # Mở rộng cửa sổ thành toàn màn hình
        self.root.state('zoomed')  # Cho Windows
        # self.root.attributes('-zoomed', True)  # Cho Linux
        # self.root.attributes('-fullscreen', True)  # Chế độ fullscreen thật (không có thanh tiêu đề)
        
        # Thiết lập style
        self.setup_styles()
        
        # Tạo puzzle
        self.puzzle = Puzzle()
        
        # Kiểm tra xem puzzle có thể giải được không
        if not self.puzzle.is_solvable():
            messagebox.showerror("Error", "This puzzle configuration is not solvable!")
        
        # Tạo giao diện
        self.create_widgets()
        
        # Biến để lưu trạng thái giải
        self.solving = False
        self.current_path = None
        self.current_step = 0
        self.start_time = 0
        self.last_algorithm = "BFS"  # Lưu thuật toán được chọn cuối cùng
        
        # Reset Solution Visualization ngay khi khởi động
        self.reset_visualization()
        
        # Dictionary lưu thống kê của các thuật toán
        self.stats = {
            "BFS": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "DFS": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "IDS": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "UCS": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "GREEDY": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "ASTAR": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "IDA": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "SHC": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "SAHC": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "BEAM": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "SA": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "STOCH": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "GA": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "ANDOR": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "SENSORLESS": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "CSP_BACKTRACKING": {"time": 0, "steps": 0, "nodes": 0, "runs": 0},
            "Q_LEARNING": {"time": 0, "steps": 0, "nodes": 0, "runs": 0}
        }
        
        # AND-OR Search window được tạo mới mỗi khi gọi hàm show_and_or_search
        
    def setup_styles(self):
        """Thiết lập styles cho giao diện"""
        style = ttk.Style()
        
        # Style cho main frame
        style.configure('Main.TFrame', background='#e8f4f8')
        
        # Style cho control frame
        style.configure('Control.TFrame', background='#ffffff')
        style.configure('Control.TLabelframe', 
                       background='#ffffff',
                       relief='solid',
                       borderwidth=1)
        style.configure('Control.TLabelframe.Label', 
                       font=('Arial', 11, 'bold'),
                       background='#ffffff',
                       foreground='#2c3e50')
        
        # Style cho buttons
        style.configure('Action.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=10,
                       width=15)
        
        # Style cho radio buttons
        style.configure('Algorithm.TRadiobutton',
                        font=('Arial', 9),  
                        background='#ffffff',
                        padding=2)  
                       
        # Style cho labels
        style.configure('Header.TLabel',
                       font=('Arial', 14, 'bold'),
                       background='#ffffff',
                       foreground='#1a5f7a')
                       
        style.configure('Stats.TLabel',
                       font=('Arial', 9),
                       background='#ffffff',
                       foreground='#34495e')
                       
        style.configure('Algorithm.TLabel',
                       font=('Arial', 10, 'bold'),
                       background='#ffffff',
                       foreground='#2980b9')
                       
        # Style cho stats frame
        style.configure('Stats.TFrame',
                       background='#ffffff',
                       relief='solid',
                       borderwidth=1)
        
    def on_algorithm_change(self, *args):
        """Xử lý sự kiện khi người dùng chọn thuật toán mới"""
        current_algorithm = self.algorithm_var.get()
        if current_algorithm != self.last_algorithm:
            self.last_algorithm = current_algorithm
            # Chỉ reset phần visualization, không reset trạng thái đầu và đích
            self.reset_visualization()
            # Highlight thuật toán đang chọn trong phần thống kê
            self.highlight_selected_algorithm(current_algorithm)
            
    def highlight_selected_algorithm(self, algorithm):
        """Đánh dấu thuật toán được chọn trong phần thống kê"""
        for algo in self.stats_labels:
            frame = self.stats_labels[algo]["frame"]
            if algo == algorithm:
                frame.configure(style='Selected.TLabelframe')
            else:
                frame.configure(style='Control.TLabelframe')
        
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        # Cấu hình style cho các thành phần
        style = ttk.Style()
        
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="20", style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)  # Sử dụng pack thay vì grid
        
        # Container frame for content
        content_frame = ttk.Frame(main_frame, style='Main.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame bên trái cho controls
        left_frame = ttk.Frame(content_frame, padding="15", style='Control.TFrame', width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Title
        title_label = ttk.Label(left_frame,
                               text="8-Puzzle Solver",
                               style='Header.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame cho algorithms
        algo_frame = ttk.LabelFrame(left_frame,
                                  text="Select Algorithm",
                                  padding="5",  # Giảm padding
                                  style='Control.TLabelframe')
        algo_frame.pack(fill="x", pady=(0, 10), ipady=0)  # Giảm khoảng cách dọc
        
        # Radio buttons cho các thuật toán
        self.algorithm_var = tk.StringVar(value="BFS")
        self.algorithm_var.trace('w', self.on_algorithm_change)  # Thêm callback
        
        # Tạo các danh sách thuật toán theo phân loại
        uninformed_algorithms = [
            ("Breadth-First Search (BFS)", "BFS"),
            ("Depth-First Search (DFS)", "DFS"),
            ("Iterative Deepening Search (IDS)", "IDS"),
            ("Uniform Cost Search (UCS)", "UCS")
        ]
        
        informed_algorithms = [
            ("Greedy Search", "GREEDY"),
            ("A* Search (A*)", "ASTAR"),
            ("IDA* Search", "IDA")
        ]
        
        local_algorithms = [
            ("Simple Hill Climbing", "SHC"),
            ("Steepest-Ascent Hill Climbing", "SAHC"),
            ("Beam Search", "BEAM"),
            ("Simulated Annealing", "SA"),
            ("Stochastic Hill Climbing", "STOCH"),
            ("Genetic Algorithm", "GA")
        ]
        
        special_algorithms = [
            ("AND-OR Search", "ANDOR"),
            ("Search with No Observation", "SENSORLESS"),
            ("Partial Observation Search", "PARTIAL")
        ]
        
        csp_algorithms = [
            ("Backtracking", "CSP_BACKTRACKING"),
            ("AC-3 Search", "CSP_AC3"),
            ("Min-Conflicts Search", "MIN_CONFLICTS")
        ]
        
        # Thêm nhóm thuật toán học tăng cường
        rl_algorithms = [
            ("Q-Learning", "Q_LEARNING")
        ]
        
        # Tạo notebook với các tab cho từng nhóm thuật toán
        notebook = ttk.Notebook(algo_frame)
        notebook.pack(fill="both", expand=True)
        
        # Tab 1: Uninformed Search
        uninformed_frame = ttk.Frame(notebook, padding=5)
        notebook.add(uninformed_frame, text="Uninformed")
        
        # Tab 2: Informed Search
        informed_frame = ttk.Frame(notebook, padding=5)
        notebook.add(informed_frame, text="Informed")
        
        # Tab 3: Local Search
        local_frame = ttk.Frame(notebook, padding=5)
        notebook.add(local_frame, text="Local")
        
        # Tab 4: Complex Environment
        special_frame = ttk.Frame(notebook, padding=5)
        notebook.add(special_frame, text="Complex Environment")
        
        # Tab 5: CSP
        csp_frame = ttk.Frame(notebook, padding=5)
        notebook.add(csp_frame, text="CSP")
        
        # Tab 6: Reinforcement Learning
        rl_frame = ttk.Frame(notebook, padding=5)
        notebook.add(rl_frame, text="Học tăng cường")
        
        # Thêm các radio button vào tab Uninformed
        for i, (text, value) in enumerate(uninformed_algorithms):
            ttk.Radiobutton(
                uninformed_frame,
                text=text,
                value=value,
                variable=self.algorithm_var,
                style='Algorithm.TRadiobutton'
            ).pack(anchor="w", pady=1)  # Giảm khoảng cách giữa các nút
        
        # Thêm các radio button vào tab Informed
        for i, (text, value) in enumerate(informed_algorithms):
            ttk.Radiobutton(
                informed_frame,
                text=text,
                value=value,
                variable=self.algorithm_var,
                style='Algorithm.TRadiobutton'
            ).pack(anchor="w", pady=1)
        
        # Thêm các radio button vào tab Local
        for i, (text, value) in enumerate(local_algorithms):
            ttk.Radiobutton(
                local_frame,
                text=text,
                value=value,
                variable=self.algorithm_var,
                style='Algorithm.TRadiobutton'
            ).pack(anchor="w", pady=1)
        
        # Thêm các radio button vào tab Specialized
        for i, (text, value) in enumerate(special_algorithms):
            ttk.Radiobutton(
                special_frame,
                text=text,
                value=value,
                variable=self.algorithm_var,
                style='Algorithm.TRadiobutton'
            ).pack(pady=1, padx=2, anchor=tk.W)
            
        # Thêm các radio button vào tab CSP
        for i, (text, value) in enumerate(csp_algorithms):
            ttk.Radiobutton(
                csp_frame,
                text=text,
                value=value,
                variable=self.algorithm_var,
                style='Algorithm.TRadiobutton'
            ).pack(pady=1, padx=2, anchor=tk.W)
            
        # Thêm các radio button vào tab Học tăng cường
        for i, (text, value) in enumerate(rl_algorithms):
            ttk.Radiobutton(
                rl_frame,
                text=text,
                value=value,
                variable=self.algorithm_var,
                style='Algorithm.TRadiobutton'
            ).pack(pady=1, padx=2, anchor=tk.W)
        
        # Frame cho controls
        control_frame = ttk.Frame(left_frame, style='Control.TFrame')
        control_frame.pack(fill="x", pady=(0, 15))
        
        # Buttons với gradient background
        solve_btn = ttk.Button(
            control_frame,
            text="Solve Puzzle",
            command=self.solve_puzzle,
            style='Action.TButton'
        )
        solve_btn.pack(pady=5, fill="x")
        
        # Thêm nút dữ liệu mẫu
        sample_data_btn = ttk.Button(
            control_frame,
            text="Dữ liệu mẫu",
            command=self.load_sample_data,
            style='Action.TButton'
        )
        sample_data_btn.pack(pady=5, fill="x")
        
        # Nút Reset Puzzle đơn giản
        reset_btn = ttk.Button(
            control_frame,
            text="Reset Puzzle",
            command=self.reset_puzzle,
            style='Action.TButton'
        )
        reset_btn.pack(pady=5, fill="x")
        

        
        # Puzzle boards ở giữa
        center_frame = ttk.Frame(content_frame, style='Main.TFrame')
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        # Tạo frame chứa các puzzle boards
        puzzle_selection_frame = ttk.Frame(center_frame, style='Main.TFrame')
        puzzle_selection_frame.pack(pady=10, fill=tk.X)
        
        # Frame cho selection puzzles
        selection_frame = ttk.LabelFrame(puzzle_selection_frame, text="Puzzle Configuration", style='Control.TLabelframe', padding=10)
        selection_frame.pack(fill=tk.X, pady=10)
        
        # Frame chứa hai puzzle boards tương tác
        interactive_boards_frame = ttk.Frame(selection_frame, style='Main.TFrame')
        interactive_boards_frame.pack(fill=tk.X, pady=5)
        
        # Board chọn trạng thái ban đầu (bên trái)
        initial_state_frame = ttk.Frame(interactive_boards_frame, style='Main.TFrame')
        initial_state_frame.pack(side=tk.LEFT, padx=10)
        self.initial_state_board = InteractivePuzzleBoard(initial_state_frame, title="Initial State", on_state_change=self.on_initial_state_change)
        self.initial_state_board.pack()
        
        # Board chọn trạng thái đích (bên phải)
        goal_state_frame = ttk.Frame(interactive_boards_frame, style='Main.TFrame')
        goal_state_frame.pack(side=tk.LEFT, padx=10)
        self.goal_state_board = InteractivePuzzleBoard(goal_state_frame, title="Goal State", on_state_change=self.on_goal_state_change)
        self.goal_state_board.pack()
        
        # Tạo frame chứa cả hai phần: Visualization và Solution Text
        solution_container = ttk.Frame(center_frame, style='Main.TFrame')
        solution_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Board hiển thị quá trình giải - đặt bên trái
        solution_frame = ttk.LabelFrame(solution_container, text="Solution Visualization", style='Control.TLabelframe', padding=15)
        solution_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Tăng kích thước tối thiểu cho solution_frame
        solution_frame.configure(height=430, width=350)  # Tăng chiều cao và rộng
        solution_frame.pack_propagate(False)  # Ngăn frame tự co lại
        
        # Style cho khung info trong solution visualization
        style.configure('SolutionInfo.TFrame', background='#e1f5fe', relief='groove', borderwidth=1)
        style.configure('SolutionInfo.TLabel', font=('Arial', 11, 'bold'), foreground='#01579b')
        
        # Tạo frame chứa puzzle board
        puzzle_container = ttk.Frame(solution_frame, style='Main.TFrame')
        puzzle_container.pack(expand=True, fill=tk.BOTH, padx=5, pady=(5, 10))
        
        # Tạo puzzle board trong container
        self.puzzle_board = PuzzleBoard(puzzle_container, cell_size=65)  # Giảm kích thước các ô puzzle
        self.puzzle_board.pack(expand=True, fill=tk.BOTH, anchor='center')
        
        # Tạo frame hiển thị text file bên phải
        self.solution_text_frame = ttk.LabelFrame(solution_container, text="Solution Details", style='Control.TLabelframe', padding=15)
        self.solution_text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.solution_text_frame.configure(height=400, width=300)
        self.solution_text_frame.pack_propagate(False)
        
        # Tạo text area có thanh cuộn
        self.solution_text = scrolledtext.ScrolledText(self.solution_text_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.solution_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.solution_text.config(state=tk.DISABLED)  # Ban đầu không cho phép chỉnh sửa
        
        # Frame bên phải cho thống kê với khả năng cuộn - giảm chiều rộng xuống còn một nửa
        right_container = ttk.Frame(content_frame, style='Main.TFrame', width=300)
        right_container.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        # Đảm bảo frame không bị mở rộng
        right_container.pack_propagate(False)
        
        # Title cho thống kê
        ttk.Label(
            right_container,
            text="Algorithm Statistics",
            style='Header.TLabel'
        ).pack(pady=(0, 15))
        
        # Canvas và scrollbar cho thống kê - giảm chiều rộng
        canvas = tk.Canvas(right_container, bg='#ffffff', highlightthickness=0, width=280)
        scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=canvas.yview)
        
        # Frame bên trong canvas để chứa thống kê
        right_frame = ttk.Frame(canvas, padding="15", style='Stats.TFrame')
        
        # Cấu hình canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Thêm right_frame vào canvas
        canvas_frame = canvas.create_window((0, 0), window=right_frame, anchor="nw")
        
        # Style cho thuật toán được chọn
        style = ttk.Style()
        style.configure('Selected.TLabelframe',
                       background='#e3f2fd',
                       relief='solid',
                       borderwidth=1)
        style.configure('Selected.TLabelframe.Label',
                       font=('Arial', 11, 'bold'),
                       background='#e3f2fd',
                       foreground='#1976d2')
        
        # Tạo labels cho thống kê
        self.stats_labels = {}
        for algo in ["BFS", "DFS", "IDS", "UCS", "GREEDY", "ASTAR", "IDA", "SHC", "SAHC", "BEAM", "SA", "STOCH", "GA", "ANDOR", "SENSORLESS", "CSP_BACKTRACKING", "CSP_AC3", "MIN_CONFLICTS"]:
            # Frame cho mỗi thuật toán
            algo_frame = ttk.LabelFrame(
                right_frame,
                text=self.get_algo_full_name(algo),
                style='Control.TLabelframe',
                padding="10",
                width=260  # Giảm chiều rộng xuống
            )
            algo_frame.pack(fill="x", pady=(0, 10))
            
            # Container cho các thông số
            stats_container = ttk.Frame(algo_frame, style='Control.TFrame')
            stats_container.pack(fill="x")
            
            # Labels cho các thông số
            self.stats_labels[algo] = {
                "frame": algo_frame,  # Lưu reference đến frame
                "time": ttk.Label(stats_container, text="⏱️ Time: 0.00s", style='Stats.TLabel'),
                "steps": ttk.Label(stats_container, text="👣 Steps: 0", style='Stats.TLabel'),
                "nodes": ttk.Label(stats_container, text="🔍 Nodes: 0", style='Stats.TLabel'),
                "runs": ttk.Label(stats_container, text="🔄 Runs: 0", style='Stats.TLabel')
            }
            
            for key, label in self.stats_labels[algo].items():
                if key != "frame":  # Không pack frame
                    label.pack(anchor="w", pady=2)
        
        # Cập nhật kích thước frame và canvas cho cuộn
        def configure_canvas(event):
            # Cập nhật kích thước window trong canvas
            canvas.itemconfig(canvas_frame, width=event.width)
            # Thiết lập vùng cuộn
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        # Bind sự kiện resize cho canvas
        canvas.bind("<Configure>", configure_canvas)
        right_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Highlight thuật toán mặc định
        self.highlight_selected_algorithm("BFS")
        
        # Hiển thị trạng thái ban đầu
        self.puzzle_board.update_board(self.puzzle.initial_state)
        
    def get_algo_full_name(self, algo):
        """Lấy tên đầy đủ của thuật toán"""
        names = {
            "BFS": "Breadth-First Search",
            "UCS": "Uniform Cost Search",
            "GREEDY": "Greedy Best-First",
            "ASTAR": "A* Search",
            "IDA": "IDA* Search",
            "SHC": "Simple Hill Climbing",
            "SAHC": "Steepest-Ascent Hill Climbing",
            "BEAM": "Beam Search",
            "SA": "Simulated Annealing",
            "STOCH": "Stochastic Hill Climbing",
            "GA": "Genetic Algorithm",
            "ANDOR": "AND-OR Search",
            "SENSORLESS": "Sensorless Search (No Observation)",
            "CSP_BACKTRACKING": "Backtracking",
            "CSP_AC3": "AC-3 Search",
            "MIN_CONFLICTS": "Min-Conflicts Search",
            "Q_LEARNING": "Q-Learning (Học tăng cường)"
        }
        return names.get(algo, algo)
        
    def update_stats(self, algorithm, solve_time, steps, nodes):
        """Cập nhật thống kê cho thuật toán"""
        stats = self.stats[algorithm]
        stats["runs"] += 1
        
        # Cập nhật thống kê trung bình
        stats["time"] = ((stats["time"] * (stats["runs"] - 1)) + solve_time) / stats["runs"]
        stats["steps"] = ((stats["steps"] * (stats["runs"] - 1)) + steps) / stats["runs"]
        stats["nodes"] = ((stats["nodes"] * (stats["runs"] - 1)) + nodes) / stats["runs"]
        
        # Cập nhật labels với màu sắc và emoji
        self.stats_labels[algorithm]["time"].config(
            text=f"⏱️ Avg Time: {stats['time']:.2f}s"
        )
        self.stats_labels[algorithm]["steps"].config(
            text=f"👣 Avg Steps: {stats['steps']:.1f}"
        )
        self.stats_labels[algorithm]["nodes"].config(
            text=f"🔍 Avg Nodes: {stats['nodes']:.1f}"
        )
        self.stats_labels[algorithm]["runs"].config(
            text=f"🔄 Total Runs: {stats['runs']}"
        )
        
    def save_solution_path(self, algorithm, path, solve_time, nodes):
        """Lưu đường đi của thuật toán ra file"""
        if not os.path.exists('solutions'):
            os.makedirs('solutions')
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"solutions/{algorithm}_{timestamp}.txt"
        
        # Chuẩn bị nội dung chi tiết của file txt
        solution_content = f"Thuật toán: {self.get_algo_full_name(algorithm)}\n"
        solution_content += f"Thời gian thực thi: {solve_time:.3f} giây\n"
        solution_content += f"Số bước: {len(path) - 1}\n"
        solution_content += f"Số nodes đã thăm: {nodes}\n"
        solution_content += "\nĐường đi:\n"
        
        for i, state in enumerate(path):
            solution_content += f"\nBước {i}:\n"
            for row in state:
                solution_content += f"{row}\n"
        
        # Lưu vào file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(solution_content)
        
        # Hiển thị nội dung trong text area
        self.display_solution_text(solution_content)
            
        messagebox.showinfo("Thành công", f"Đã lưu và hiển thị đường đi từ {filename}")

    def solve_puzzle(self):
        """Thực hiện giải puzzle theo thuật toán đã chọn"""
        # Cập nhật trạng thái ban đầu và đích của puzzle
        initial_state = self.initial_state_board.get_state()
        goal_state = self.goal_state_board.get_state()
        
        if not initial_state or not goal_state:
            messagebox.showerror("Lỗi", "Vui lòng thiết lập trạng thái ban đầu và trạng thái đích!")
            return
            
        # Nếu chọn các thuật toán đặc biệt, mở cửa sổ riêng thay vì chạy thuật toán ở giao diện chính
        selected_algorithm = self.algorithm_var.get()
        if selected_algorithm == "ANDOR":
            self.show_and_or_search()
            return
        elif selected_algorithm == "SENSORLESS":
            self.show_sensorless_search()
            return
        elif selected_algorithm == "PARTIAL":
            self.show_partial_observation_search()
            return
        elif selected_algorithm == "CSP_BACKTRACKING":
            # Gọi hàm mà không truyền tham số vì hàm này không nhận tham số
            show_backtracking_visualization()
            return
        elif selected_algorithm == "CSP_AC3":
            # Thêm xử lý cho thuật toán AC-3
            from algorithms.csp_ac3 import show_ac3_visualization
            show_ac3_visualization()
            return
        elif selected_algorithm == "MIN_CONFLICTS":
            from algorithms.csp_min_conflicts import show_min_conflicts_visualization
            show_min_conflicts_visualization()
            return
        elif selected_algorithm == "Q_LEARNING":
            self.show_q_learning(initial_state, goal_state)
            return
        
        # Bắt đầu theo dõi thời gian
        start_time = time.time()
        
        # Tạo đối tượng puzzle với trạng thái ban đầu và đích
        puzzle = Puzzle(initial_state)
        # Đặt trạng thái đích tùy chỉnh
        puzzle.goal_state = goal_state
        
        # Kiểm tra xem có thể đi từ trạng thái đầu đến trạng thái đích hay không
        # Tính số đảo trong cả hai trạng thái
        def count_inversions(state):
            flat_state = [num for row in state for num in row]
            inversions = 0
            for i in range(len(flat_state)):
                for j in range(i + 1, len(flat_state)):
                    if flat_state[i] != 0 and flat_state[j] != 0 and flat_state[i] > flat_state[j]:
                        inversions += 1
            return inversions
        
        initial_inversions = count_inversions(initial_state)
        goal_inversions = count_inversions(goal_state)
        
        # Hai trạng thái có thể đạt đến nhau nếu cùng chẵn hoặc cùng lẻ
        if (initial_inversions % 2) != (goal_inversions % 2):
            messagebox.showerror("Error", "This puzzle configuration is impossible to solve! The goal state cannot be reached from the initial state.")
            return
        
        try:
            # Gọi thuật toán tương ứng
            algo = self.algorithm_var.get()
            path = None
            nodes_explored = 0
            
            if algo == "BFS":
                path, nodes_explored = bfs_search(puzzle)
            elif algo == "DFS":
                path, nodes_explored = dfs_search(puzzle, max_depth=50)
            elif algo == "IDS":
                path, nodes_explored = ids_search(puzzle, max_depth=30)
            elif algo == "UCS":
                path, nodes_explored = ucs_search(puzzle)
            elif algo == "GREEDY":
                path, nodes_explored = greedy_search(puzzle)
            elif algo == "ASTAR":
                path, nodes_explored = astar_search(puzzle)
            elif algo == "IDA":
                path, nodes_explored = ida_star_search(puzzle)
            elif algo == "SHC":
                path, nodes_explored = simple_hill_climbing(puzzle)
            elif algo == "SAHC":
                path, nodes_explored = steepest_hill_climbing(puzzle)
            elif algo == "BEAM":
                path, nodes_explored = beam_search(puzzle, beam_width=3)
            elif algo == "SA":
                path, nodes_explored = simulated_annealing(puzzle)
            elif algo == "STOCH":
                path, nodes_explored = stochastic_hill_climbing(puzzle)
            elif algo == "GA":
                path, nodes_explored = genetic_algorithm(puzzle, pop_size=200, max_generations=200)
        
            # Tính thời gian giải
            solve_time = time.time() - start_time
            
            if path:
                # Cập nhật thống kê
                self.update_stats(algo, solve_time, len(path) - 1, nodes_explored)
                
                # Lưu trữ đường đi và các thông tin liên quan
                self.current_path = path
                self.current_step = 0
                
                # Lưu thời gian bắt đầu để tính thời gian hiển thị
                self.start_time = time.time()
                
                # Lưu đường đi vào file
                self.save_solution_path(algo, path, solve_time, nodes_explored)
                
                # Hiển thị trạng thái ban đầu trước tiên trong phần visualization
                self.puzzle_board.update_board(initial_state)
                self.puzzle_board.update_info(0, 0.0)
                
                # Đợi 1 giây trước khi bắt đầu hiển thị các bước tiếp theo
                self.root.after(1000, self.show_solution)
            else:
                # Hiển thị thông báo nếu không tìm thấy lời giải
                messagebox.showinfo("No Solution", "No solution found!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def reset_visualization(self):
        """Chỉ reset bảng visualization mà không reset trạng thái đầu và đích"""
        # Reset bảng visualization
        self.puzzle_board.update_board([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.puzzle_board.update_info(0, 0.0)
        
        # Reset các biến liên quan tới lời giải
        self.current_path = None
        self.current_step = 0
        
        # Xóa nội dung text area
        self.display_solution_text("Chưa có kết quả giải thuật toán.\n\nHãy điền trạng thái đầu, trạng thái đích và chọn 'Solve Puzzle'!")
        

    
    def reset_puzzle(self):
        """Đặt lại toàn bộ puzzle về trạng thái ban đầu"""
        # Reset bảng visualization
        self.reset_visualization()
        
        # Reset trạng thái ban đầu và đích
        self.initial_state_board.reset_board()
        self.goal_state_board.reset_board()
    
    def on_initial_state_change(self, state):
        """Xử lý khi trạng thái ban đầu thay đổi"""
        pass
        
    def on_goal_state_change(self, state):
        """Xử lý khi trạng thái đích thay đổi"""
        pass
    
    def load_sample_data(self):
        """Nạp dữ liệu mẫu cho trạng thái đầu và trạng thái đích"""
        # Trạng thái ban đầu mẫu từ hình ảnh
        initial_state = [
            [2, 6, 5],
            [0, 8, 7],
            [4, 3, 1]
        ]
        
        # Trạng thái đích mẫu từ hình ảnh
        goal_state = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        
        # Cập nhật các bảng
        self.initial_state_board.set_state(initial_state)
        self.goal_state_board.set_state(goal_state)
        
        # Hiển thị thông báo
        messagebox.showinfo("Dữ liệu mẫu", "Dữ liệu mẫu đã được nạp thành công!")
        
    def display_solution_text(self, content):
        """Hiển thị nội dung file txt trong khu vực solution text"""
        # Cho phép chỉnh sửa để cập nhật nội dung
        self.solution_text.config(state=tk.NORMAL)
        # Xóa nội dung cũ
        self.solution_text.delete(1.0, tk.END)
        # Thêm nội dung mới
        self.solution_text.insert(tk.END, content)
        # Trở lại trạng thái chỉ đọc
        self.solution_text.config(state=tk.DISABLED)
        # Cuộn lên đầu
        self.solution_text.see(1.0)
        
    def show_and_or_search(self):
        """Hiển thị cửa sổ tìm kiếm AND-OR."""
        from ui.and_or_search_window_new import AndOrSearchWindow
        AndOrSearchWindow(self.root)
    
    def show_sensorless_search(self):
        """Hiển thị cửa sổ tìm kiếm Sensorless (Không quan sát)."""
        from ui.sensorless_search_window import SensorlessSearchWindow
        SensorlessSearchWindow(self.root)
    
    def show_partial_observation_search(self):
        """Hiển thị cửa sổ tìm kiếm Partial Observation (Quan sát một phần)."""
        from ui.partial_observation_search_window import PartialObservationSearchWindow
        PartialObservationSearchWindow(self.root)
        
    def show_q_learning(self, initial_state, goal_state):
        """Hiển thị cửa sổ Q-learning với tiến trình huấn luyện tích hợp."""
        # Các tham số huấn luyện mặc định
        learning_params = {
            "alpha": 0.1,  # Learning rate
            "gamma": 0.9,  # Discount factor
            "epsilon": 0.3,  # Exploration rate
            "episodes": 1000,  # Số lượt huấn luyện
            "shuffle_steps": 20  # Số bước trộn cho mỗi trạng thái ban đầu mới
        }
        
        # Hiển thị cửa sổ trực quan hóa Q-learning với tiến trình huấn luyện tích hợp
        show_qlearning_visualization(initial_state, goal_state, learning_params)

    def show_solution(self):
        """Hiển thị từng bước của giải pháp"""
        try:
            if not self.current_path or self.current_step >= len(self.current_path):
                return
                
            # Lấy trạng thái hiện tại
            current_state = self.current_path[self.current_step]
            
            # Cập nhật bảng puzzle
            self.puzzle_board.update_board(current_state)
            
            # Tính thời gian đã trôi qua
            elapsed_time = time.time() - self.start_time
            
            # Cập nhật thông tin
            self.puzzle_board.update_info(self.current_step, elapsed_time)
            
            # Tăng bước hiện tại
            self.current_step += 1
            
            # Hiển thị bước tiếp theo sau 0.5 giây nếu còn bước
            if self.current_step < len(self.current_path):
                self.root.after(500, self.show_solution)
            else:
                # Đã hiển thị xong tất cả các bước
                messagebox.showinfo("Hoàn thành", "Puzzle đã được giải thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")