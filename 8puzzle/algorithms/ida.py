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
   
    if not puzzle.is_solvable():
        return None, 0
    threshold = manhattan_distance(puzzle.initial_state, puzzle.goal_state)
    path = [puzzle.initial_state]
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
