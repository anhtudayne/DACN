"""Thuật toán Tìm kiếm AND-OR (AND-OR Search) cho bài toán 8-puzzle trong môi trường không xác định"""
import numpy as np
import copy
import random

def get_possible_results(puzzle, state, action, success_prob=0.9):
    
    results = []
    
    # Thử hành động thành công (90%)
    try:
        success_state = puzzle.apply_move(copy.deepcopy(state), action)
        results.append((success_state, success_prob))
    except ValueError:
        # Nếu hành động không thể thực hiện, cũng coi như không di chuyển
        results.append((copy.deepcopy(state), success_prob))
    
    # Xác suất còn lại (10%) chia đều cho các trường hợp thất bại
    failure_prob = (1 - success_prob) / 2
    
    # Trường hợp thất bại 1: Không di chuyển
    results.append((copy.deepcopy(state), failure_prob))
    
    # Trường hợp thất bại 2: Di chuyển kép
    try:
        # Áp dụng cùng một hành động hai lần
        double_move_state = copy.deepcopy(state)
        double_move_state = puzzle.apply_move(double_move_state, action)
        double_move_state = puzzle.apply_move(double_move_state, action)
        results.append((double_move_state, failure_prob))
    except ValueError:
        # Nếu di chuyển kép không thể thực hiện, tăng xác suất cho "không di chuyển"
        results[1] = (results[1][0], results[1][1] + failure_prob)
    
    return results

def and_or_graph_search(puzzle, max_depth=30, max_nodes=10000, success_prob=0.9):
    
    
    # Biến đếm số nút đã mở rộng
    nodes_expanded = [0]
    
    def or_search(state, path, depth):
        """Xử lý nút OR - chọn hành động tốt nhất từ trạng thái hiện tại"""
        # Tăng số nút đã mở rộng
        nodes_expanded[0] += 1
        
        # Kiểm tra giới hạn
        if nodes_expanded[0] >= max_nodes:
            return None
        
        # Kiểm tra nếu đạt tới trạng thái đích
        if puzzle.is_goal(state):
            return {"type": "action", "action": "goal", "next": None}
        
        # Kiểm tra độ sâu
        if depth <= 0:
            return None
        
        # Kiểm tra chu trình - sử dụng so sánh cụ thể hơn thay vì np.array_equal
        for prev_state in path:
            is_same = True
            for i in range(len(state)):
                for j in range(len(state[i])):
                    if state[i][j] != prev_state[i][j]:
                        is_same = False
                        break
                if not is_same:
                    break
            if is_same:
                return None
        
        # Thử từng hành động có thể
        for action in puzzle.get_possible_moves(state):
            # Xác định các kết quả có thể của hành động
            results = get_possible_results(puzzle, state, action, success_prob)
            
            # Tìm kiếm kế hoạch cho các kết quả (nút AND)
            result_states = [r[0] for r in results]
            plan = and_search(result_states, path + [state], depth - 1)
            
            # Nếu tìm được kế hoạch thành công, trả về
            if plan is not None:
                return {"type": "action", "action": action, "next": plan}
        
        # Không tìm thấy kế hoạch
        return None
    
    def and_search(states, path, depth):
        """Xử lý nút AND - phải tìm kế hoạch cho tất cả các trạng thái có thể"""
        # Nếu không có trạng thái, trả về kế hoạch rỗng
        if not states:
            return None
        
        # Tìm kiếm kế hoạch cho từng trạng thái
        plans = []
        for s in states:
            plan = or_search(s, path, depth)
            
            # Nếu một trạng thái không có kế hoạch, trả về thất bại
            if plan is None:
                return None
            
            plans.append((s, plan))
        
        # Trả về kế hoạch điều kiện cho nút AND
        return {"type": "contingency", "subplans": plans}
    
    # Bắt đầu tìm kiếm từ trạng thái ban đầu
    return or_search(puzzle.initial_state, [], max_depth)

def format_conditional_plan(plan, puzzle, indent=0):
    """
    Định dạng kế hoạch điều kiện thành văn bản có thể đọc được.
    
    Tham số:
    - plan: Kế hoạch điều kiện (cây AND-OR)
    - puzzle: Đối tượng Puzzle
    - indent: Số khoảng trắng thụt đầu dòng
    
    Trả về:
    - Chuỗi biểu diễn kế hoạch
    """
    if plan is None:
        return " " * indent + "Không tìm thấy kế hoạch\n"
    
    prefix = " " * indent
    
    if plan["type"] == "action" and plan["action"] == "goal":
        return prefix + "✅ Đã đạt đến trạng thái đích!\n"
    
    if plan["type"] == "action":
        action_str = prefix + f"🔹 Thực hiện hành động: {plan['action']}\n"
        next_str = format_conditional_plan(plan["next"], puzzle, indent + 2)
        return action_str + next_str
    
    if plan["type"] == "contingency":
        result = prefix + "🔸 Nếu sau khi thực hiện hành động:\n"
        for i, (state, subplan) in enumerate(plan["subplans"]):
            state_str = format_state(state)
            result += prefix + f"  - Kết quả {i+1}: {state_str}\n"
            result += format_conditional_plan(subplan, puzzle, indent + 4)
        return result
    
    return prefix + "Định dạng kế hoạch không hợp lệ\n"

def format_state(state):
    """
    Định dạng trạng thái thành chuỗi dễ đọc.
    
    Tham số:
    - state: Trạng thái cần định dạng
    
    Trả về:
    - Chuỗi biểu diễn trạng thái
    """
    flat_state = [cell for row in state for cell in row]
    return "[" + " ".join(str(x) for x in flat_state) + "]"

def find_path_to_goal(plan, puzzle):
    """
    Tìm một đường đi đến trạng thái đích từ kế hoạch điều kiện.
    Lưu ý: Đây là một đường đi có thể, không phải tất cả các đường đi có thể.
    
    Tham số:
    - plan: Kế hoạch điều kiện
    - puzzle: Đối tượng Puzzle
    
    Trả về:
    - Danh sách các trạng thái từ ban đầu đến đích, hoặc None nếu không có đường đi
    """
    if plan is None:
        return None
    
    if plan["type"] == "action" and plan["action"] == "goal":
        return [puzzle.goal_state]
    
    if plan["type"] == "action":
        action = plan["action"]
        # Giả định hành động thành công (kết quả đầu tiên)
        try:
            next_state = puzzle.apply_move(puzzle.initial_state, action)
            rest_path = find_path_to_goal(plan["next"], puzzle)
            if rest_path:
                return [puzzle.initial_state] + rest_path
        except:
            pass
    
    if plan["type"] == "contingency":
        # Chọn kế hoạch đầu tiên để minh họa
        if plan["subplans"]:
            state, subplan = plan["subplans"][0]
            rest_path = find_path_to_goal(subplan, puzzle)
            if rest_path:
                return [state] + rest_path
    
    return None
