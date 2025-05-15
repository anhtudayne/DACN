"""IDA* Search implementation for 8-puzzle"""
from .heuristics import manhattan_distance

class Node:
    def __init__(self, state, parent=None, move=None, g=0):
        self.state = state          # Trạng thái hiện tại của puzzle
        self.parent = parent        # Nút cha
        self.move = move            # Bước đi dẫn đến trạng thái này
        self.g = g                  # Chi phí từ trạng thái đầu đến trạng thái hiện tại
        self.h = 0                  # Giá trị heuristic (khoảng cách Manhattan đến đích)
        self.f = 0                  # Tổng chi phí (f = g + h)

def ida_star_search(puzzle):
    """
    Thuật toán IDA* (Iterative Deepening A*) cho bài toán 8-puzzle.
    
    Định nghĩa:
    IDA* (Iterative Deepening A*) là một thuật toán tìm kiếm thông minh, kết hợp ưu điểm của A* và Iterative Deepening.
    
    Nguyên lý hoạt động:
    - Sử dụng kỹ thuật “tăng dần ngưỡng” (iterative deepening) dựa trên giá trị f = g + h.
    - Thực hiện nhiều lần DFS với ngưỡng cost giới hạn tăng dần.
    - Tại mỗi vòng lặp, chỉ khám phá các nút có tổng chi phí f ≤ ngưỡng hiện tại.
    - Ngưỡng mới là giá trị f nhỏ nhất vượt quá ngưỡng hiện tại trong vòng lặp trước.
    
    Ưu điểm:
    - Đảm bảo tìm ra đường đi tối ưu (ngắn nhất) giống như A*.
    - Tiết kiệm bộ nhớ hơn so với A* vì không cần duy trì hàng đợi ưu tiên.
    - Đặc biệt hiệu quả trong các bài toán có không gian trạng thái lớn, khó lưu trữ toàn bộ biên.
    
    Nhược điểm:
    - Có thể phải khám phá lại nhiều nút ở các vòng lặp khác nhau.
    - Trường hợp xấu nhất có thể chậm hơn A* vì phải lặp lại công việc.
    
    Trả về:
        (path, nodes_explored): Đường đi từ trạng thái đầu đến đích, số nút đã khám phá
        hoặc (None, nodes_explored) nếu không tìm thấy đường đi
    """
    # Kiểm tra tính giải được của puzzle
    if not puzzle.is_solvable():
        return None, 0

    # Thiết lập ngưỡng ban đầu bằng giá trị heuristic của trạng thái đầu
    threshold = manhattan_distance(puzzle.initial_state, puzzle.goal_state)
    # Đường đi hiện tại (ban đầu chỉ có trạng thái khởi đầu)
    path = [puzzle.initial_state]
    # Sử dụng list để có thể thay đổi giá trị trong hàm đệ quy
    nodes_explored = [0]

    def search(path, g, threshold):
        """Hàm tìm kiếm đệ quy cho IDA*"""
        # Lấy trạng thái hiện tại từ cuối đường đi
        node = path[-1]
        # Tính tổng chi phí f = g + h
        # g: Chi phí từ trạng thái đầu đến hiện tại
        # h: Ước lượng khoảng cách từ hiện tại đến đích (heuristic)
        f = g + manhattan_distance(node, puzzle.goal_state)

        # Nếu f vượt quá ngưỡng, trả về giá trị f để cập nhật ngưỡng mới
        if f > threshold:
            return f

        # Nếu đạt đến trạng thái đích, trả về kết quả thành công
        if puzzle.is_goal(node):
            return "FOUND"

        # Khởi tạo ngưỡng nhỏ nhất tiếp theo
        min_threshold = float('inf')
        # Khám phá tất cả các bước đi có thể từ trạng thái hiện tại
        for move in puzzle.get_possible_moves(node):
            try:
                # Tạo trạng thái mới từ bước đi
                new_state = puzzle.apply_move(node, move)
                # Tránh trường hợp quay lại trạng thái đã đi qua trên đường đi hiện tại
                if new_state not in path:  # Tránh vòng lặp
                    # Thêm trạng thái mới vào đường đi
                    path.append(new_state)
                    # Tăng số nút đã khám phá
                    nodes_explored[0] += 1
                    # Tiếp tục tìm kiếm đệ quy với độ sâu tăng thêm 1
                    temp = search(path, g + 1, threshold)
                    # Nếu tìm thấy đường đi tới đích, trả về kết quả
                    if temp == "FOUND":
                        return "FOUND"
                    # Cập nhật ngưỡng nhỏ nhất cho lần lặp tiếp theo
                    if temp < min_threshold:
                        min_threshold = temp
                    # Quay lại: loại bỏ trạng thái hiện tại khỏi đường đi
                    path.pop()
            except ValueError:
                continue  # Bỏ qua các bước đi không hợp lệ

        # Trả về ngưỡng mới cho lần lặp tiếp theo
        return min_threshold

    # Vòng lặp chính của thuật toán IDA*
    while True:
        # Thực hiện tìm kiếm với ngưỡng hiện tại
        temp = search(path, 0, threshold)
        # Nếu tìm thấy đường đi đến đích
        if temp == "FOUND":
            return path, nodes_explored[0]
        # Nếu không còn đường đi nào để khám phá
        if temp == float('inf'):
            return None, nodes_explored[0]
        # Tăng ngưỡng lên giá trị mới tìm được cho lần lặp tiếp theo
        threshold = temp
