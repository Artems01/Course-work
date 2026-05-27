import numpy as np
from functions_game import get_stone_groups, has_no_liberties


class MinimaxAgent:
    def __init__(self, color="white", depth=1):
        """
        Агент на основе алгоритма Минимакс.
        """
        self.color = color
        self.is_black = True if color == "black" else False
        self.depth = depth

    def get_valid_moves(self, board):
        moves = []
        for col in range(board.shape[0]):
            for row in range(board.shape[1]):
                if board[col, row] == 0:
                    moves.append((col, row))
        return moves

    def count_liberties(self, board, group):
        liberties = set()
        for x, y in group:
            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            for nx, ny in neighbors:
                if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                    if board[nx, ny] == 0:
                        liberties.add((nx, ny))
        return len(liberties)

    def capture_stones(self, board, color):
        captured = 0
        for group in list(get_stone_groups(board, color)):
            if has_no_liberties(board, group):
                for i, j in group:
                    board[i, j] = 0
                    captured += 1
        return captured

    def simulate_move(self, board, move, is_black_turn):
        new_board = np.copy(board)
        col, row = move
        player = 1 if is_black_turn else 2
        enemy_color = "white" if is_black_turn else "black"

        new_board[col, row] = player
        captures = self.capture_stones(new_board, enemy_color)
        return new_board, captures

    def evaluate(self, board, is_black_player):
        my_color = "black" if is_black_player else "white"
        enemy_color = "white" if is_black_player else "black"
        score = 0

        # Оценка своих групп
        for group in get_stone_groups(board, my_color):
            liberties = self.count_liberties(board, group)
            score += liberties * 15
            score += len(group) * 3

        # Оценка вражеских групп
        for group in get_stone_groups(board, enemy_color):
            liberties = self.count_liberties(board, group)
            score -= liberties * 10
            score -= len(group) * 2
            if liberties == 1:
                score += 200  # Бонус за атари

        return score

    def minimax(self, board, depth, maximizing_player, is_current_turn_black):
        valid_moves = self.get_valid_moves(board)

        if depth == 0 or not valid_moves:
            return self.evaluate(board, self.is_black), None

        best_move = None

        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                new_board, captures = self.simulate_move(board, move, is_current_turn_black)

                if captures > 0:
                    return 999999, move

                # Передаем инвертированный ход для противника (следующий уровень дерева)
                eval_score, _ = self.minimax(new_board, depth - 1, False, not is_current_turn_black)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            return max_eval, best_move

        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board, captures = self.simulate_move(board, move, is_current_turn_black)

                if captures > 0:
                    return -999999, move

                # Передаем инвертированный ход для противника
                eval_score, _ = self.minimax(new_board, depth - 1, True, not is_current_turn_black)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            return min_eval, best_move

    def choose_action(self, game_env):
        """
        Интерфейсный метод для интеграции с окружением.
        """
        board = game_env.game.board
        # Передаем текущий флаг хода (is_black) агента
        _, move = self.minimax(board, self.depth, True, self.is_black)

        if move is None:
            valid_moves = self.get_valid_moves(board)
            if valid_moves:
                move = valid_moves[0]
            else:
                return None

        return move[0] * game_env.size + move[1]