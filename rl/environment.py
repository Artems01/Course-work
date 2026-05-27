import os
import sys
import numpy as np

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from game import Game

class AtariGoEnv:

    def __init__(self, size=9):

        self.size = size

        self.game = Game(
            board_size=(size, size)
        )

        self.max_moves = size * size

        self.reset()

    def reset(self):

        self.game.board = np.zeros(
            (self.size, self.size),
            dtype=int
        )

        self.game.black_turn = True

        self.game.prisoners = {
            'black': 0,
            'white': 0
        }

        self.moves_count = 0

        return self.get_state()

    def get_state(self):

        return tuple(
            self.game.board.flatten()
        )

    def get_valid_actions(self):

        actions = []

        for col in range(self.size):

            for row in range(self.size):

                if self.game.is_valid_move(col, row):

                    action = col * self.size + row

                    actions.append(action)

        return actions

    def step(self, action):

        col = action // self.size
        row = action % self.size

        if not self.game.is_valid_move(col, row):

            return self.get_state(), -20, True, {}

        current_player = (
            'black'
            if self.game.black_turn
            else 'white'
        )

        before_black = self.game.prisoners['black']
        before_white = self.game.prisoners['white']

        self.game.place_stone(col, row)

        after_black = self.game.prisoners['black']
        after_white = self.game.prisoners['white']

        reward = -0.1

        if current_player == 'black':

            captured = after_black - before_black

        else:

            captured = after_white - before_white

        if captured > 0:

            reward += 100

        winner = self.game.check_winner()

        done = False

        if winner:

            done = True

            if winner.lower() == current_player:

                reward += 500

            else:

                reward -= 500

        self.moves_count += 1
        if self.moves_count >= self.max_moves:
            done = True

        self.game.black_turn = (
            not self.game.black_turn
        )

        return (
            self.get_state(),
            reward,
            done,
            {}
        )