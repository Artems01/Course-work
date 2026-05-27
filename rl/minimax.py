import numpy as np

from functions_game import (
    get_stone_groups,
    has_no_liberties
)

class MinimaxAgent:

    def __init__(self,
                 color='white',
                 depth=2):

        self.color = color

        self.is_black = (
            color == 'black'
        )

        self.depth = depth

    def get_valid_moves(self, board):

        moves = []

        for col in range(board.shape[0]):

            for row in range(board.shape[1]):

                if board[col, row] == 0:

                    moves.append(
                        (col, row)
                    )

        return moves

    def count_liberties(self,
                         board,
                         group):

        liberties = set()

        for x, y in group:

            neighbors = [
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1)
            ]

            for nx, ny in neighbors:

                if (
                    0 <= nx < board.shape[0]
                    and
                    0 <= ny < board.shape[1]
                ):

                    if board[nx, ny] == 0:

                        liberties.add(
                            (nx, ny)
                        )

        return len(liberties)

    def capture_stones(self,
                       board,
                       color):

        captured = 0

        for group in list(
            get_stone_groups(board, color)
        ):

            if has_no_liberties(
                board,
                group
            ):

                for i, j in group:

                    board[i, j] = 0

                    captured += 1

        return captured

    def simulate_move(self,
                      board,
                      move,
                      is_black_turn):

        new_board = np.copy(board)

        col, row = move

        player = (
            1
            if is_black_turn
            else 2
        )

        enemy_color = (
            'white'
            if is_black_turn
            else 'black'
        )

        new_board[col, row] = player

        captures = self.capture_stones(
            new_board,
            enemy_color
        )

        return new_board, captures

    def evaluate(self, board):

        my_color = (
            'black'
            if self.is_black
            else 'white'
        )

        enemy_color = (
            'white'
            if self.is_black
            else 'black'
        )

        score = 0

        for group in get_stone_groups(
            board,
            my_color
        ):

            liberties = self.count_liberties(
                board,
                group
            )

            score += liberties * 20

        for group in get_stone_groups(
            board,
            enemy_color
        ):

            liberties = self.count_liberties(
                board,
                group
            )

            score -= liberties * 15

            if liberties == 1:

                score += 200

        return score

    def minimax(self,
                board,
                depth,
                maximizing,
                is_black_turn):

        valid_moves = self.get_valid_moves(
            board
        )

        if (
            depth == 0
            or
            not valid_moves
        ):

            return self.evaluate(board), None

        best_move = None

        if maximizing:

            best_score = float('-inf')

            for move in valid_moves:

                new_board, captures = (
                    self.simulate_move(
                        board,
                        move,
                        is_black_turn
                    )
                )

                if captures > 0:

                    return 999999, move

                score, _  = self.minimax(
                    new_board,
                    depth - 1,
                    False,
                    not is_black_turn
                )

                if score > best_score:

                    best_score = score

                    best_move = move

            return best_score, best_move

        else:

            best_score = float('inf')

            for move in valid_moves:

                new_board, captures = (
                    self.simulate_move(
                        board,
                        move,
                        is_black_turn
                    )
                )

                score, _ = self.minimax(
                    new_board,
                    depth - 1,
                    True,
                    not is_black_turn
                )

                if score < best_score:

                    best_score = score

                    best_move = move

            return best_score, best_move

    def choose_action(self, env):

        _, move = self.minimax(
            env.game.board,
            self.depth,
            True,
            self.is_black
        )

        if move is None:

            return None

        col, row = move

        return (
            col * env.size + row
        )