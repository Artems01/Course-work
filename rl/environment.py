import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from contants import WINNING_SCORE

class AtariGoEnv:
    def __init__(self, size=9):
        self.size = size
        self.game = Game(board_size=(size, size))
        self.reset()

    def reset(self):
        self.game.board = np.zeros((self.size, self.size), dtype=int)
        self.game.black_turn = True
        self.game.prisoners = {'black': 0, 'white': 0}
        self.game.game_over = False
        return self._get_state_string()

    def _get_state_string(self):
        return "".join(map(str, self.game.board.flatten()))

    def get_valid_actions(self):
        valid_actions = []
        for col in range(self.size):
            for row in range(self.size):
                if self.game.is_valid_move(col, row):
                    action_id = col * self.size + row
                    valid_actions.append(action_id)
        return valid_actions

    def step(self, action_id, agent_color="black"):
        col = action_id // self.size
        row = action_id % self.size

        if not self.game.is_valid_move(col, row):
            return self._get_state_string(), -10.0, True, {}

        opp_color = "white" if agent_color == "black" else "black"
        prisoners_before = self.game.prisoners[agent_color]
        lost_before = self.game.prisoners[opp_color]

        self.game.place_stone(col, row)

        captured = self.game.prisoners[agent_color] - prisoners_before
        we_lost = self.game.prisoners[opp_color] - lost_before

        reward = -0.1
        if captured > 0:
            reward += 15.0 * captured
        if we_lost > 0:
            reward -= 15.0 * we_lost

        winner = self.game.check_winner()
        done = False

        if winner is not None:
            done = True
            if winner.lower() == agent_color:
                reward += 50.0
            else:
                reward -= 50.0
        elif not self.get_valid_actions():
            done = True

        return self._get_state_string(), reward, done, {}