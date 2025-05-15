"""8-puzzle model implementation"""
import random

class Puzzle:
    def __init__(self, initial_state=None):
        # Goal state as shown in the image
        self.goal_state = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        
        # Default initial state as shown in the image
        self.default_initial_state = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 0, 8]
        ]
        
        if initial_state:
            if not self.is_valid_state(initial_state):
                raise ValueError("Invalid initial state")
            self.initial_state = initial_state
        else:
            self.initial_state = self.default_initial_state
            
    def is_valid_state(self, state):
        """Check if state is valid (3x3 grid with numbers 0-8)"""
        if len(state) != 3 or any(len(row) != 3 for row in state):
            return False
            
        numbers = []
        for row in state:
            numbers.extend(row)
        return sorted(numbers) == list(range(9))
            
    def generate_solvable_state(self):
        """Generate a random solvable puzzle state"""
        while True:
            numbers = list(range(9))
            random.shuffle(numbers)
            state = [numbers[i:i+3] for i in range(0, 9, 3)]
            self.initial_state = state
            if self.is_solvable():
                return state
        
    def is_solvable(self):
        """Check if the puzzle is solvable using inversion count"""
        flat_initial = [num for row in self.initial_state for num in row]
        inversions = 0
        
        for i in range(len(flat_initial)):
            for j in range(i + 1, len(flat_initial)):
                if flat_initial[i] != 0 and flat_initial[j] != 0 and flat_initial[i] > flat_initial[j]:
                    inversions += 1
                    
        return inversions % 2 == 0
        
    def get_blank_pos(self, state):
        """Get position of blank (0) in state"""
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return i, j
        raise ValueError("Invalid state: no blank position found")
        
    def get_possible_moves(self, state):
        """Get list of possible moves (up, down, left, right)"""
        moves = []
        i, j = self.get_blank_pos(state)
        
        if i > 0: moves.append('up')
        if i < 2: moves.append('down')
        if j > 0: moves.append('left')
        if j < 2: moves.append('right')
        
        return moves
        
    def apply_move(self, state, move):
        """Apply move to state and return new state"""
        if move not in self.get_possible_moves(state):
            raise ValueError(f"Invalid move: {move}")
            
        new_state = [row[:] for row in state]
        i, j = self.get_blank_pos(state)
        
        if move == 'up':    i2, j2 = i-1, j
        elif move == 'down':  i2, j2 = i+1, j
        elif move == 'left':  i2, j2 = i, j-1
        else:  # right
            i2, j2 = i, j+1
        
        new_state[i][j], new_state[i2][j2] = new_state[i2][j2], new_state[i][j]
        return new_state
        
    def get_state_string(self, state):
        """Convert state to string for comparison"""
        return ''.join(str(num) for row in state for num in row)
        
    def is_goal(self, state):
        """Check if state is goal state"""
        # So sánh từng phần tử thay vì so sánh trực tiếp cả nested list
        if not state or not self.goal_state:
            return False
            
        for i in range(len(state)):
            for j in range(len(state[i])):
                if state[i][j] != self.goal_state[i][j]:
                    return False
        return True