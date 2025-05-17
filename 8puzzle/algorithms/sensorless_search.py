
import time
from models.sensorless_puzzle import SensorlessPuzzle

class SensorlessSearch:
 
    
    def __init__(self, puzzle, max_depth=30, max_time=10):
      
        self.puzzle = puzzle
        self.max_depth = max_depth
        self.max_time = max_time
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        self.expanded_initial_belief_state = None
        self.time_limit_reached = False
    
    def search(self):
        """
        Thực hiện thuật toán tìm kiếm BFS.
        
        Returns:
            Đường đi từ initial belief state đến goal belief state,
            hoặc None nếu không tìm thấy hoặc vượt quá thời gian giới hạn.
        """
        # Reset các biến theo dõi
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        self.time_limit_reached = False
        
        # Lưu thời gian bắt đầu tìm kiếm
        start_time = time.time()
        
        # Initial belief state
        initial_belief_state = self.puzzle.get_initial_belief_state()
        
        # Kiểm tra thời gian giới hạn cho toàn bộ quá trình
        def check_time_limit():
            if time.time() - start_time > self.max_time:
                print(f"Giới hạn thời gian ({self.max_time} giây) đã được vượt quá.")
                self.time_limit_reached = True
                return True
            return False
        
        # Ban đầu, ta có initial_belief_state là danh sách các trạng thái
        # Các expanded belief states sẽ là các cặp trạng thái mới sau khi áp dụng các hành động
        expanded_belief_states = []
        # Đầu tiên, thêm initial belief state vào danh sách các belief states để so sánh
        expanded_belief_states.append(initial_belief_state)
        
        # Áp dụng các hành động (UP, DOWN, LEFT, RIGHT) cho cả belief state
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        for action in actions:
            # Kiểm tra thời gian giới hạn trước mỗi lần mở rộng
            if check_time_limit():
                # Trả về ngay nếu đã vượt quá thời gian giới hạn
                return None
                
            # Áp dụng hành động lên toàn bộ belief state
            new_belief_state = self.puzzle.apply_action(initial_belief_state, action)
            
            # Kiểm tra xem belief state mới có trùng với bất kỳ belief state nào trong expanded_belief_states không
            is_duplicate = False
            for existing_belief_state in expanded_belief_states:
                if self._is_same_belief_state(existing_belief_state, new_belief_state):
                    is_duplicate = True
                    break
            
            # Nếu không trùng lặp, thêm vào expanded_belief_states
            if not is_duplicate:
                expanded_belief_states.append(new_belief_state)
        
        # Lấy expanded initial belief state (loại bỏ initial belief state gốc)
        expanded_initial_belief_state = expanded_belief_states[1:]
        
        # Nếu không có expanded belief states, sử dụng initial belief state
        if not expanded_initial_belief_state:
            expanded_initial_belief_state = [initial_belief_state]
        
        # Lưu trữ expanded initial belief state để hiển thị trên giao diện
        self.expanded_initial_belief_state = expanded_initial_belief_state
        
        print(f"Initial belief state size: {len(initial_belief_state)}")
        print(f"Expanded belief state size: {len(expanded_initial_belief_state)}")
        
        # QUAN TRỌNG: Không kiểm tra goal ở đây, phải chạy BFS để tìm giải pháp
        
        # Bắt đầu BFS với initial belief state (sau khi đã mở rộng)
        # Mỗi phần tử trong frontier là (belief_state, path)
        # Bắt đầu với các belief state mở rộng từ initial belief state
        frontier = []
        explored = set()
        
        # Thêm các belief state đã mở rộng vào frontier
        for i, belief_state in enumerate(expanded_initial_belief_state):
            # Đối với mỗi belief state, thêm vào frontier với đường đi ban đầu
            if i == 0:  # belief state đầu tiên (UP)
                frontier.append((belief_state, ["UP"]))
            elif i == 1:  # belief state thứ hai (DOWN)
                frontier.append((belief_state, ["DOWN"]))
            elif i == 2:  # belief state thứ ba (LEFT)
                frontier.append((belief_state, ["LEFT"]))
            elif i == 3:  # belief state thứ tư (RIGHT)
                frontier.append((belief_state, ["RIGHT"]))
                
        # Nếu frontier rỗng, khởi tạo với expanded_initial_belief_state
        if not frontier:
            # Sử dụng empty path - sẽ được cập nhật khi áp dụng hành động
            frontier = [(expanded_initial_belief_state[0], [])]
        
        while frontier:
            # Kiểm tra thời gian giới hạn trong mỗi lần lặp
            if check_time_limit():
                return None
                
            self.max_frontier_size = max(self.max_frontier_size, len(frontier))
            
            # Lấy belief state từ frontier (BFS)
            current_belief_state, path = frontier.pop(0)
            
            # Kiểm tra độ sâu
            if len(path) >= self.max_depth:
                continue
            
            # Chuyển belief state thành hash để kiểm tra đã khám phá chưa
            bs_hash = self._belief_state_to_hash(current_belief_state)
            if bs_hash in explored:
                continue
            
            # Thêm vào explored
            explored.add(bs_hash)
            self.nodes_expanded += 1
            
            # Lấy các hành động có thể
            actions = self.puzzle.get_actions(current_belief_state)
            
            # Thử từng hành động
            for action in actions:
                # Tính belief state mới
                new_belief_state = self.puzzle.apply_action(current_belief_state, action)
                
                # Kiểm tra goal
                if self.puzzle.is_goal(new_belief_state):
                    return path + [action]
                
                # Thêm vào frontier
                frontier.append((new_belief_state, path + [action]))
        
        # Không tìm thấy đường đi
        return None
    
    def _is_same_belief_state(self, belief_state1, belief_state2):
        """
        Kiểm tra xem hai belief states có giống nhau không.
        Hai belief states được coi là giống nhau nếu chúng chứa các trạng thái giống nhau
        (không phụ thuộc vào thứ tự).
        """
        # Nếu số lượng trạng thái khác nhau, hai belief states không thể giống nhau
        if len(belief_state1) != len(belief_state2):
            return False
            
        # So sánh các trạng thái trong belief states
        # Chuyển các belief states thành tập hợp để so sánh
        set1 = {tuple(map(tuple, state)) for state in belief_state1}
        set2 = {tuple(map(tuple, state)) for state in belief_state2}
        
        # Nếu hai tập hợp giống nhau, hai belief states giống nhau
        return set1 == set2
    
    def _belief_state_to_hash(self, belief_state):
        """
        Chuyển đổi belief state thành hash để lưu trữ trong explored.
        Vì belief state là một tập hợp, nên thứ tự các trạng thái không quan trọng.
        Do đó, chúng ta sắp xếp các trạng thái để đảm bảo tính nhất quán.
        """
        # Sắp xếp các trạng thái để đảm bảo tính nhất quán
        sorted_states = sorted([str(state) for state in belief_state])
        return tuple(sorted_states)
    
    def get_statistics(self):
        """Trả về thống kê của quá trình tìm kiếm."""
        return {
            'nodes_expanded': self.nodes_expanded,
            'max_frontier_size': self.max_frontier_size,
            'expanded_belief_state_size': len(self.expanded_initial_belief_state) if self.expanded_initial_belief_state else 0,
            'time_limit_reached': self.time_limit_reached
        }
        
    def get_expanded_initial_belief_state(self):
        """Trả về expanded initial belief state."""
        return self.expanded_initial_belief_state
