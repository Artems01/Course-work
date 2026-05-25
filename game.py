import pygame
import sys
from contants import BOARD_WIDTH, WINNING_SCORE
from functions_game import xy_to_colrow, has_no_liberties, get_stone_groups


class Game:

    def __init__(self, screen_size=(600, 600), board_size=(18, 18)):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.board_size = board_size
        self.cell_size = screen_size[0] // board_size[0]
        self.board = [[None for _ in range(board_size[1])] for _ in range(board_size[0])]
        self.current_player = "black"  # "black" or "white"
        self.font = pygame.font.SysFont("arial", 36)
        self.game_over = False

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 30)
        self.place_sound = pygame.mixer.Sound("move_fishki.wav")
        pygame.mixer.init()  # Инициализация модуля микширования

    def pass_move(self):
        self.black_turn = not self.black_turn
        self.draw()

    def handle_click(self):
        x, y = pygame.mouse.get_pos()

        col, row = xy_to_colrow(x, y, self.size)

        if not self.is_valid_move(col, row):
            return

        self.place_stone(col, row)
        self.place_sound.play()
        winner = self.check_winner()
        if winner:
            self.show_winner_message(winner)

        self.black_turn = not self.black_turn
        self.draw()

    def is_valid_move(self, col, row):
        """Check if placing a stone at (col, row) is valid."""
        if col < 0 or col >= self.board.shape[0] or row < 0 or row >= self.board.shape[0]:
            return False
        return self.board[col, row] == 0

    def place_stone(self, col, row):
        """Places a stone on the board and handles captures."""
        player = 1 if self.black_turn else 2
        self.board[col, row] = player
        self.handle_captures()

    def handle_captures(self):
        """Handles captures for both players after each move."""
        self_color = "black" if self.black_turn else "white"
        other_color = "white" if self.black_turn else "black"

        captured_count = self.capture_stones(other_color)
        self.prisoners[self_color] += captured_count

    def capture_stones(self, color):
        """Captures stones of the specified color."""
        color_code = 1 if color == "black" else 2
        captured_count = 0
        for group in list(get_stone_groups(self.board, color)):
            if has_no_liberties(self.board, group):
                for i, j in group:
                    self.board[i, j] = 0
                    captured_count += 1
        return captured_count

    def check_winner(self):
        """Checks if either player has reached the winning score."""
        if self.prisoners['black'] >= WINNING_SCORE:
            return "Black"
        elif self.prisoners['white'] >= WINNING_SCORE:
            return "White"
        else:
            return None

    def show_winner_message(self, winner):
        """Показывает сообщение о выигрыше."""
        font = pygame.font.Font(None, 74)
        text = font.render(f"{winner} wins!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

        # Заливка фона
        self.screen.fill((0, 0, 0))  # Черный фон
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        # Ждем, пока пользователь не закроет окно
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Нажмите Enter для выхода
                        waiting = False