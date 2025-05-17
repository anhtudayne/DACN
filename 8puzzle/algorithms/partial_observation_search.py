

import time
from models.partial_observation_puzzle import PartialObservationPuzzle

class PartialObservationSearch:
    
    def __init__(self, puzzle, max_depth=30, max_time=10):
       
        self.puzzle = puzzle
        self.max_depth = max_depth
        self.max_time = max_time
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        self.time_limit_reached = False
        self.expanded_initial_belief_state = None
    
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
        
        # Hàm kiểm tra thời gian giới hạn
        def check_time_limit():
            if time.time() - start_time > self.max_time:
                print(f"Giới hạn thời gian ({self.max_time} giây) đã được vượt quá.")
                self.time_limit_reached = True
                return True
            return False
        
        # Initial belief state
        initial_belief_state = self.puzzle.get_initial_belief_state()
        
        # Mở rộng initial belief state - trong trường hợp partial observation chúng ta không cần mở rộng
        self.expanded_initial_belief_state = initial_belief_state
        
        # Không kiểm tra goal ở đây, phải chạy BFS để tìm giải pháp
        
        # Bắt đầu với initial belief state
        frontier = [(initial_belief_state, [])]
        # Explored là tập hợp các belief state đã khám phá
        explored = set()
        
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
            
            # Kiểm tra belief state có hợp lệ không
            if not current_belief_state or not isinstance(current_belief_state, list) or len(current_belief_state) == 0:
                print(f"Lỗi: Belief state không hợp lệ: {current_belief_state}")
                continue
                
            # Chuyển belief state thành hash để kiểm tra đã khám phá chưa
            try:
                bs_hash = self._belief_state_to_hash(current_belief_state)
                if bs_hash in explored:
                    continue
            except Exception as e:
                print(f"Lỗi khi hash belief state: {e}")
                continue
            
            # Thêm vào explored
            explored.add(bs_hash)
            self.nodes_expanded += 1
            
            # Lấy các hành động có thể
            try:
                actions = self.puzzle.get_actions(current_belief_state)
            except Exception as e:
                print(f"Lỗi khi lấy hành động: {e}")
                continue
            
            # Thử từng hành động
            for action in actions:
                # Kiểm tra thời gian giới hạn trước mỗi hành động
                if check_time_limit():
                    return None
                    
                try:
                    # Tính belief state mới
                    new_belief_state = self.puzzle.apply_action(current_belief_state, action)
                    
                    # Kiểm tra belief state mới có hợp lệ không
                    if not new_belief_state or len(new_belief_state) == 0:
                        continue
                        
                    # Kiểm tra goal
                    if self.puzzle.is_goal(new_belief_state):
                        return path + [action]
                    
                    # Thêm vào frontier
                    frontier.append((new_belief_state, path + [action]))
                except Exception as e:
                    print(f"Lỗi khi xử lý hành động {action}: {e}")
                    continue
        
        # Không tìm thấy đường đi
        return None
    
    def _belief_state_to_hash(self, belief_state):
       
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
