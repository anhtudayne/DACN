"""Thuật toán Di truyền (Genetic Algorithm) cho bài toán 8-puzzle"""
from .heuristics import manhattan_distance, misplaced_tiles
import random
import time
import numpy as np
import copy

class Chromosome:
   
    def __init__(self, moves=None, puzzle=None, initial_state=None):
        self.moves = moves if moves else []  # Chuỗi các bước di chuyển
        self.puzzle = puzzle  # Đối tượng puzzle
        self.initial_state = initial_state  # Trạng thái ban đầu
        self.fitness = 0  # Độ thích nghi (càng thấp càng tốt)
        self.fitness_calculated = False  # Đánh dấu đã tính độ thích nghi chưa
        self.final_state = None  # Trạng thái cuối cùng sau khi áp dụng tất cả các bước di chuyển
    
    def calculate_fitness(self, heuristic_func=manhattan_distance):
        """
        Tính độ thích nghi của cá thể.
        Độ thích nghi = heuristic(trạng thái cuối) + độ dài chuỗi di chuyển (để ưu tiên lời giải ngắn)
        """
        if self.fitness_calculated:
            return self.fitness
        
        # Áp dụng các bước di chuyển để có trạng thái cuối cùng
        current_state = copy.deepcopy(self.initial_state)
        valid_moves = 0
        visited_states = set()  # Theo dõi các trạng thái đã thăm để tránh chu trình
        visited_states.add(str(current_state))  # Thêm trạng thái ban đầu
        
        for move in self.moves:
            try:
                # Thử áp dụng bước di chuyển
                new_state = self.puzzle.apply_move(current_state, move)
                
                # Kiểm tra nếu trạng thái mới đã được thăm (chu trình)
                state_str = str(new_state)
                if state_str in visited_states:
                    continue  # Bỏ qua bước di chuyển này
                
                # Cập nhật trạng thái hiện tại và đánh dấu đã thăm
                current_state = new_state
                visited_states.add(state_str)
                valid_moves += 1
                
                # Nếu đã đạt đến trạng thái đích, dừng
                if self.puzzle.is_goal(current_state):
                    break
                    
            except ValueError:
                # Bỏ qua các bước di chuyển không hợp lệ
                continue
        
        self.final_state = current_state
        
        # Tính độ thích nghi với trọng số khác nhau
        h_value = heuristic_func(current_state, self.puzzle.goal_state)
        
        # Nếu đạt được trạng thái đích, ưu tiên cao hơn nhiều
        if self.puzzle.is_goal(current_state):
            # Đạt đích và ngắn => fitness thấp (tốt)
            self.fitness = 0.1 * valid_moves
        else:
            # Không đạt đích, độ thích nghi phụ thuộc vào khoảng cách và độ dài
            self.fitness = h_value * 10 + valid_moves * 0.1
        
        self.fitness_calculated = True
        return self.fitness
    
    def is_solution(self):
        """Kiểm tra xem cá thể có phải là lời giải"""
        if not self.final_state:
            return False
        
        # Kiểm tra chặt chẽ hơn
        is_goal = self.puzzle.is_goal(self.final_state)
        
        # Nếu đang báo cáo là lời giải, kiểm tra lại để chắc chắn
        if is_goal:
            # Tính lại đường đi để đảm bảo tính đúng đắn
            path = self.get_path()
            if path and len(path) > 1:
                return self.puzzle.is_goal(path[-1])
        
        return is_goal
    
    def get_path(self):
        """Trả về đường đi từ trạng thái ban đầu đến trạng thái cuối cùng"""
        if not self.final_state:
            return None
        
        # Áp dụng lại các bước di chuyển và lưu lại các trạng thái trung gian
        path = [copy.deepcopy(self.initial_state)]
        current_state = copy.deepcopy(self.initial_state)
        visited_states = set()  # Theo dõi các trạng thái đã thăm để tránh chu trình
        visited_states.add(str(current_state))  # Thêm trạng thái ban đầu
        
        for move in self.moves:
            try:
                new_state = self.puzzle.apply_move(current_state, move)
                
                # Kiểm tra trạng thái mới đã được thăm chưa (tránh chu trình)
                state_str = str(new_state)
                if state_str in visited_states:
                    continue
                
                # Cập nhật trạng thái hiện tại và đánh dấu đã thăm
                current_state = new_state
                visited_states.add(state_str)
                path.append(copy.deepcopy(current_state))
                
                # Nếu đã đạt đến trạng thái đích, dừng
                if self.puzzle.is_goal(current_state):
                    break
                    
            except ValueError:
                continue
        
        # Kiểm tra nếu đường đi không đạt đến trạng thái đích
        if not self.puzzle.is_goal(path[-1]):
            return None
            
        return path

def initialize_population(puzzle, pop_size=100, max_chromosome_length=50):
   
    population = []
    
    # Tạo một số cá thể "thông minh" dựa trên các hành động hợp lệ
    smart_count = min(pop_size // 4, 10)  # 25% quần thể hoặc tối đa 10 cá thể thông minh
    
    for i in range(pop_size):
        # Với 25% đầu tiên của quần thể, tạo cá thể thông minh hơn
        if i < smart_count:
            # Bắt đầu từ trạng thái ban đầu và thực hiện các bước di chuyển có ý nghĩa
            current_state = copy.deepcopy(puzzle.initial_state)
            moves = []
            visited_states = set([str(current_state)])
            
            # Thực hiện một chuỗi bước đi hợp lệ (không có chu trình)
            for _ in range(random.randint(max_chromosome_length//2, max_chromosome_length)):
                # Lấy tất cả các bước di chuyển có thể từ trạng thái hiện tại
                possible_moves = puzzle.get_possible_moves(current_state)
                
                if not possible_moves:
                    break  # Không có bước di chuyển hợp lệ
                
                # Chọn một bước di chuyển ngẫu nhiên
                move = random.choice(possible_moves)
                moves.append(move)
                
                try:
                    # Áp dụng bước di chuyển
                    new_state = puzzle.apply_move(current_state, move)
                    
                    # Kiểm tra chu trình
                    state_str = str(new_state)
                    if state_str in visited_states:
                        break  # Tránh chu trình
                    
                    # Cập nhật trạng thái và đánh dấu đã thăm
                    current_state = new_state
                    visited_states.add(state_str)
                    
                    # Nếu đã đạt đến đích, dừng
                    if puzzle.is_goal(current_state):
                        break
                        
                except ValueError:
                    continue
        else:
            # Tạo cá thể hoàn toàn ngẫu nhiên
            length = random.randint(1, max_chromosome_length)
            moves = []
            
            for _ in range(length):
                move = random.choice(['up', 'down', 'left', 'right'])
                moves.append(move)
        
        # Tạo cá thể mới và thêm vào quần thể
        chromosome = Chromosome(moves=moves, puzzle=puzzle, initial_state=puzzle.initial_state)
        population.append(chromosome)
    
    return population

def selection(population, tournament_size=5):
    """
    Chọn lọc các cá thể tốt hơn bằng phương pháp chọn lọc giải đấu.
    
    Tham số:
    - population: Danh sách các cá thể
    - tournament_size: Kích thước của mỗi giải đấu
    
    Trả về:
    - Cá thể được chọn
    """
    # Chọn ngẫu nhiên một số cá thể từ quần thể
    tournament = random.sample(population, min(tournament_size, len(population)))
    
    # Chọn cá thể có độ thích nghi cao nhất (giá trị fitness thấp nhất)
    return min(tournament, key=lambda x: x.calculate_fitness())

def crossover(parent1, parent2, crossover_rate=0.8):
    """
    Lai ghép hai cá thể cha mẹ để tạo ra hai cá thể con.
    
    Tham số:
    - parent1, parent2: Hai cá thể cha mẹ
    - crossover_rate: Tỷ lệ lai ghép
    
    Trả về:
    - Hai cá thể con
    """
    # Nếu không lai ghép, trả về bản sao của cha mẹ
    if random.random() > crossover_rate:
        child1 = Chromosome(moves=parent1.moves.copy(), puzzle=parent1.puzzle, initial_state=parent1.initial_state)
        child2 = Chromosome(moves=parent2.moves.copy(), puzzle=parent2.puzzle, initial_state=parent2.initial_state)
        return child1, child2
    
    # Chọn loại lai ghép: điểm lai hoặc lai ghép đồng nhất
    crossover_type = random.choices(['point', 'uniform'], weights=[0.7, 0.3], k=1)[0]
    
    if crossover_type == 'point':  # Lai ghép điểm
        min_length = min(len(parent1.moves), len(parent2.moves))
        if min_length <= 1:
            # Nếu một trong hai cha mẹ có chuỗi quá ngắn, tạo bản sao
            child1 = Chromosome(moves=parent1.moves.copy(), puzzle=parent1.puzzle, initial_state=parent1.initial_state)
            child2 = Chromosome(moves=parent2.moves.copy(), puzzle=parent2.puzzle, initial_state=parent2.initial_state)
        else:
            # Lai ghép hai điểm
            if min_length > 3 and random.random() < 0.5:  # 50% cơ hội dùng lai ghép hai điểm
                # Chọn hai điểm cắt
                point1 = random.randint(1, min_length // 2)
                point2 = random.randint(point1 + 1, min_length - 1)
                
                # Tạo chuỗi di chuyển cho các con
                child1_moves = parent1.moves[:point1] + parent2.moves[point1:point2] + parent1.moves[point2:]
                child2_moves = parent2.moves[:point1] + parent1.moves[point1:point2] + parent2.moves[point2:]
            else:  # Lai ghép một điểm
                # Chọn điểm cắt ngẫu nhiên
                crossover_point = random.randint(1, min_length - 1)
                
                # Tạo chuỗi di chuyển cho các con
                child1_moves = parent1.moves[:crossover_point] + parent2.moves[crossover_point:]
                child2_moves = parent2.moves[:crossover_point] + parent1.moves[crossover_point:]
            
            # Tạo các cá thể con
            child1 = Chromosome(moves=child1_moves, puzzle=parent1.puzzle, initial_state=parent1.initial_state)
            child2 = Chromosome(moves=child2_moves, puzzle=parent2.puzzle, initial_state=parent2.initial_state)
    
    else:  # Lai ghép đồng nhất (uniform crossover)
        max_length = max(len(parent1.moves), len(parent2.moves))
        child1_moves = []
        child2_moves = []
        
        # Chọn từng gene từ một trong hai cha mẹ
        for i in range(max_length):
            # Quyết định lấy gene từ cha mẹ nào
            if random.random() < 0.5:  # 50% cơ hội
                # Lấy từ parent1 cho child1, parent2 cho child2
                if i < len(parent1.moves):
                    child1_moves.append(parent1.moves[i])
                if i < len(parent2.moves):
                    child2_moves.append(parent2.moves[i])
            else:
                # Lấy từ parent2 cho child1, parent1 cho child2
                if i < len(parent2.moves):
                    child1_moves.append(parent2.moves[i])
                if i < len(parent1.moves):
                    child2_moves.append(parent1.moves[i])
        
        # Tạo các cá thể con
        child1 = Chromosome(moves=child1_moves, puzzle=parent1.puzzle, initial_state=parent1.initial_state)
        child2 = Chromosome(moves=child2_moves, puzzle=parent2.puzzle, initial_state=parent2.initial_state)
    
    return child1, child2

def mutation(chromosome, mutation_rate=0.1, max_length_change=3):
    """
    Đột biến một cá thể bằng cách thay đổi ngẫu nhiên một số bước di chuyển
    hoặc thêm/xóa một số bước di chuyển.
    
    Tham số:
    - chromosome: Cá thể cần đột biến
    - mutation_rate: Tỷ lệ đột biến của mỗi bước di chuyển
    - max_length_change: Số lượng bước tối đa có thể thêm hoặc xóa
    
    Trả về:
    - Cá thể đã đột biến
    """
    # Chọn chiến lược đột biến
    mutation_strategy = random.choices(['standard', 'smart', 'sequence'], weights=[0.5, 0.3, 0.2], k=1)[0]
    
    moves = chromosome.moves.copy()
    
    if mutation_strategy == 'standard':
        # Đột biến tiêu chuẩn: Thay đổi ngẫu nhiên các bước di chuyển
        for i in range(len(moves)):
            if random.random() < mutation_rate:
                moves[i] = random.choice(['up', 'down', 'left', 'right'])
        
        # Thêm hoặc xóa các bước di chuyển
        length_change = random.randint(-max_length_change, max_length_change)
        
        if length_change > 0:
            # Thêm bước di chuyển
            for _ in range(length_change):
                move = random.choice(['up', 'down', 'left', 'right'])
                insert_position = random.randint(0, len(moves))
                moves.insert(insert_position, move)
        elif length_change < 0 and len(moves) > abs(length_change):
            # Xóa bước di chuyển
            for _ in range(abs(length_change)):
                del_position = random.randint(0, len(moves) - 1)
                moves.pop(del_position)
    
    elif mutation_strategy == 'smart':
        # Đột biến thông minh: Áp dụng để kiểm tra tính hợp lệ của từng bước di chuyển
        if len(moves) > 0:
            # Bắt đầu từ trạng thái ban đầu
            current_state = copy.deepcopy(chromosome.puzzle.initial_state)
            new_moves = []
            
            # Áp dụng các bước di chuyển và kiểm tra tính hợp lệ
            for i in range(len(moves)):
                if random.random() < mutation_rate:  # Đột biến bước di chuyển này
                    # Lấy các bước di chuyển hợp lệ từ trạng thái hiện tại
                    possible_moves = chromosome.puzzle.get_possible_moves(current_state)
                    if possible_moves:
                        # Chọn một bước di chuyển hợp lệ thay thế
                        move = random.choice(possible_moves)
                        new_moves.append(move)
                        try:
                            current_state = chromosome.puzzle.apply_move(current_state, move)
                        except ValueError:
                            continue
                    else:
                        # Giữ nguyên bước di chuyển
                        new_moves.append(moves[i])
                else:
                    # Giữ nguyên bước di chuyển
                    new_moves.append(moves[i])
                    try:
                        current_state = chromosome.puzzle.apply_move(current_state, moves[i])
                    except ValueError:
                        continue
            
            moves = new_moves
    
    else:  # sequence mutation
        # Đột biến chuỗi: Đảo ngược, xoay hoặc thay thế một chuỗi con
        if len(moves) > 3:  # Chỉ áp dụng nếu đủ dài
            # Chọn kiểu đột biến chuỗi
            seq_mutation = random.choice(['reverse', 'rotate', 'replace'])
            
            # Chọn vị trí bắt đầu và độ dài chuỗi con
            max_seq_len = min(len(moves) // 2, 5)  # Tối đa 5 bước hoặc nửa chuỗi
            seq_len = random.randint(2, max_seq_len)
            start_pos = random.randint(0, len(moves) - seq_len)
            
            if seq_mutation == 'reverse':
                # Đảo ngược chuỗi con
                sub_sequence = moves[start_pos:start_pos + seq_len]
                sub_sequence.reverse()
                moves[start_pos:start_pos + seq_len] = sub_sequence
            
            elif seq_mutation == 'rotate':
                # Xoay chuỗi con sang phải 1 vị trí
                sub_sequence = moves[start_pos:start_pos + seq_len]
                rotated = [sub_sequence[-1]] + sub_sequence[:-1]  # Xoay phải 1 vị trí
                moves[start_pos:start_pos + seq_len] = rotated
            
            else:  # replace
                # Thay thế chuỗi con bằng các bước ngẫu nhiên mới
                new_sub_sequence = []
                for _ in range(seq_len):
                    new_sub_sequence.append(random.choice(['up', 'down', 'left', 'right']))
                moves[start_pos:start_pos + seq_len] = new_sub_sequence
    
    # Tạo cá thể mới đã đột biến
    mutated = Chromosome(moves=moves, puzzle=chromosome.puzzle, initial_state=chromosome.initial_state)
    return mutated

def genetic_algorithm(puzzle, heuristic_func=manhattan_distance, pop_size=100, max_generations=100, tournament_size=5, elite_size=10, mutation_rate=0.1, crossover_rate=0.7, max_chromosome_length=50, early_stopping=20, max_time=30):
    
    if not puzzle.is_solvable():
        return None, 0
    
    start_time = time.time()
    
    # Khởi tạo quần thể ban đầu
    population = initialize_population(puzzle, pop_size=pop_size)
    
    # Số nút đã khám phá (mỗi cá thể tính là một nút)
    nodes_explored = pop_size
    
    # Biến lưu trữ cá thể tốt nhất
    best_chromosome = None
    
    # Tiến hóa qua các thế hệ
    for generation in range(max_generations):
        # Kiểm tra thời gian chạy
        if time.time() - start_time > max_time:
            break
        
        # Đánh giá độ thích nghi của toàn bộ quần thể
        for chromosome in population:
            chromosome.calculate_fitness(heuristic_func)
        
        # Sắp xếp quần thể theo độ thích nghi (từ thấp đến cao)
        population.sort(key=lambda x: x.fitness)
        
        # Lưu lại cá thể tốt nhất của thế hệ hiện tại
        current_best = population[0]
        
        # Cập nhật cá thể tốt nhất tổng thể
        if not best_chromosome or current_best.fitness < best_chromosome.fitness:
            best_chromosome = copy.deepcopy(current_best)
        
        # Kiểm tra xem đã tìm thấy lời giải chưa
        if current_best.is_solution():
            return current_best.get_path(), nodes_explored
        
        # Tạo quần thể mới
        new_population = []
        
        # Giữ lại một số cá thể tốt nhất (tinh hoa)
        elite_count = max(2, int(pop_size * 0.1))  # 10% quần thể
        new_population.extend([copy.deepcopy(chromosome) for chromosome in population[:elite_count]])
        
        # Tạo phần còn lại của quần thể mới thông qua chọn lọc, lai ghép và đột biến
        while len(new_population) < pop_size:
            # Chọn lọc cá thể cha mẹ
            parent1 = selection(population, tournament_size)
            parent2 = selection(population, tournament_size)
            
            # Lai ghép để tạo cá thể con
            child1, child2 = crossover(parent1, parent2, crossover_rate)
            
            # Đột biến cá thể con
            child1 = mutation(child1, mutation_rate)
            child2 = mutation(child2, mutation_rate)
            
            # Thêm cá thể con vào quần thể mới
            new_population.append(child1)
            if len(new_population) < pop_size:
                new_population.append(child2)
            
            # Cập nhật số nút đã khám phá
            nodes_explored += 2
        
        # Thay thế quần thể cũ bằng quần thể mới
        population = new_population
    
    # Kiểm tra lần cuối xem có tìm thấy lời giải không
    # Đánh giá toàn bộ quần thể một lần nữa
    for chromosome in population:
        chromosome.calculate_fitness(heuristic_func)
        if chromosome.is_solution():
            return chromosome.get_path(), nodes_explored
    
    # Nếu có best_chromosome và nó là lời giải, trả về
    if best_chromosome and best_chromosome.is_solution():
        return best_chromosome.get_path(), nodes_explored
    
    # Không tìm thấy lời giải
    return None, nodes_explored
