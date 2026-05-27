import pygame
import numpy as np
import itertools
import sys
import networkx as nx
import collections
from pygame import gfxdraw

# Game constants
BOARD_BROWN = (194, 105, 42)
BOARD_WIDTH = 700
BOARD_BORDER = 45
STONE_RADIUS = 14
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TURN_POS = (BOARD_BORDER, 20)
SCORE_POS = (BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER + 30)
DOT_RADIUS = 4
WINNING_SCORE = 1

def make_grid(size):
    start_points, end_points = [], []
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_BORDER)
    start_points += list(zip(xs, ys))

    xs = np.full((size), BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    start_points += list(zip(xs, ys))

    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    end_points += list(zip(xs, ys))

    xs = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    end_points += list(zip(xs, ys))

    return (start_points, end_points)

def xy_to_colrow(x, y, size):
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x_dist = x - BOARD_BORDER
    y_dist = y - BOARD_BORDER
    col = int(round(x_dist / inc))
    row = int(round(y_dist / inc))
    return col, row

def colrow_to_xy(col, row, size):
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x = int(BOARD_BORDER + col * inc)
    y = int(BOARD_BORDER + row * inc)
    return x, y

def has_no_liberties(board, group):
    for x, y in group:
        if x > 0 and board[x - 1, y] == 0:
            return False
        if y > 0 and board[x, y - 1] == 0:
            return False
        if x < board.shape[0] - 1 and board[x + 1, y] == 0:
            return False
        if y < board.shape[0] - 1 and board[x, y + 1] == 0:
            return False
    return True

def get_stone_groups(board, color):
    size = board.shape[0]
    color_code = 1 if color == "black" else 2
    xs, ys = np.where(board == color_code)
    graph = nx.grid_graph(dim=[size, size])
    stones = set(zip(xs, ys))
    all_spaces = set(itertools.product(range(size), range(size)))
    stones_to_remove = all_spaces - stones
    graph.remove_nodes_from(stones_to_remove)
    return nx.connected_components(graph)

def draw_menu(screen, font):
    """Отрисовка главного меню с поддержкой новых режимов ИИ."""
    screen.fill((0, 0, 0))
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    button_width = int(screen_width * 0.5)
    button_height = 45
    button_padding = 20
    button_color = (100, 100, 255)
    text_color = (255, 255, 255)

    start_y = 100

    # 1. PvP режим
    pvp_rect = pygame.Rect((screen_width - button_width) // 2, start_y, button_width, button_height)
    pygame.draw.rect(screen, button_color, pvp_rect)
    txt = font.render("Играть (Игрок vs Игрок)", True, text_color)
    screen.blit(txt, txt.get_rect(center=pvp_rect.center))

    # 2. Против Q-learning
    ai_qa_rect = pygame.Rect((screen_width - button_width) // 2, start_y + (button_height + button_padding), button_width, button_height)
    pygame.draw.rect(screen, button_color, ai_qa_rect)
    txt = font.render("Играть против Q-Агента", True, text_color)
    screen.blit(txt, txt.get_rect(center=ai_qa_rect.center))

    # 3. Против Минимакса
    ai_minimax_rect = pygame.Rect((screen_width - button_width) // 2, start_y + 2 * (button_height + button_padding), button_width, button_height)
    pygame.draw.rect(screen, button_color, ai_minimax_rect)
    txt = font.render("Играть против Minimax", True, text_color)
    screen.blit(txt, txt.get_rect(center=ai_minimax_rect.center))

    # 4. Правила игры
    rules_rect = pygame.Rect((screen_width - button_width) // 2, start_y + 3 * (button_height + button_padding), button_width, button_height)
    pygame.draw.rect(screen, button_color, rules_rect)
    txt = font.render("Правила игры", True, text_color)
    screen.blit(txt, txt.get_rect(center=rules_rect.center))

    pygame.display.flip()
    return pvp_rect, ai_qa_rect, ai_minimax_rect, rules_rect

def show_rules(screen):
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 28)
    rules = [
        "Правила игры:",
        "• Игра проводится на доске размера 18x18 (или заданной);",
        "• Ходы выполняются по очереди;",
        "• Играют два игрока: один использует черные фишки, другой — белые.",
        "• Игроки поочередно ставят свои фишки на пересечения линий на доске.",
        "• Фишка или группа фишек противника, окруженные фишками соперника, снимаются.",
        "• Побеждает игрок, первым окруживший хотя бы один камень противника."
    ]
    for i, line in enumerate(rules):
        text = font.render(line, True, (0, 0, 0))
        screen.blit(text, (20, 20 + i * 30))

    back_button_rect = pygame.Rect(20, 20 + len(rules) * 30 + 30, 200, 40)
    pygame.draw.rect(screen, (100, 100, 255), back_button_rect)
    back_text = font.render("Главное меню", True, (255, 255, 255))
    screen.blit(back_text, back_text.get_rect(center=back_button_rect.center))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if back_button_rect.collidepoint(event.pos):
                    waiting = False

class Game:
    def __init__(self, size):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.black_turn = True
        self.prisoners = collections.defaultdict(int)
        self.start_points, self.end_points = make_grid(self.size)

        # Переменные интеграции ИИ
        self.game_over = False
        self.game_mode = "pvp"  # "pvp", "ai_qa", "ai_minimax"
        self.ai_agent = None
        self.minimax_agent = None

    def start(self):
        self.init_pygame()
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("arial", 24)

        while True:
            pvp_r, qa_r, mini_r, rules_r = draw_menu(self.screen, font)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if pvp_r.collidepoint(event.pos):
                        self.game_mode = "pvp"
                        self.play_game()
                        return
                    elif qa_r.collidepoint(event.pos):
                        self.game_mode = "ai_qa"
                        self.play_game()
                        return
                    elif mini_r.collidepoint(event.pos):
                        self.game_mode = "ai_minimax"
                        self.play_game()
                        return
                    elif rules_r.collidepoint(event.pos):
                        show_rules(self.screen)

            clock.tick(30)

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
        pygame.display.set_caption("Atari-Go с интеграцией ИИ")
        self.font = pygame.font.SysFont("arial", 30)
        try:
            self.place_sound = pygame.mixer.Sound("move_fishki.wav")
        except:
            self.place_sound = None  # Защита, если звукового файла нет рядом
        pygame.mixer.init()

    def play_game(self):
        self.clear_screen()
        self.draw()
        clock = pygame.time.Clock()

        # ОСНОВНОЙ ИГРОВОЙ ЦИКЛ (с обработкой кликов человека)
        while not self.game_over:
            # 1. Если сейчас ход Человека (Черных) ИЛИ режим PvP (где оба люди)
            if self.black_turn or self.game_mode == "pvp":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.handle_click()

            # 2. Если сейчас ход Компьютера (Белых) в режимах с ИИ
            else:
                self.update()

            clock.tick(30)

        # Ожидание закрытия после конца игры
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def clear_screen(self):
        self.screen.fill(BOARD_BROWN)
        for start_point, end_point in zip(self.start_points, self.end_points):
            pygame.draw.line(self.screen, BLACK, start_point, end_point)

        guide_dots = [3, self.size // 2, self.size - 4]
        for col, row in itertools.product(guide_dots, guide_dots):
            if col < self.size and row < self.size:
                x, y = colrow_to_xy(col, row, self.size)
                gfxdraw.aacircle(self.screen, x, y, DOT_RADIUS, BLACK)
                gfxdraw.filled_circle(self.screen, x, y, DOT_RADIUS, BLACK)

    def handle_click(self):
        x, y = pygame.mouse.get_pos()
        col, row = xy_to_colrow(x, y, self.size)

        if not self.is_valid_move(col, row):
            return

        self.place_stone(col, row)
        if self.place_sound:
            self.place_sound.play()

        winner = self.check_winner()
        if winner:
            self.game_over = True
            self.show_winner_message(winner)
            return

        self.black_turn = not self.black_turn
        self.draw()

    def is_valid_move(self, col, row):
        if col < 0 or col >= self.board.shape[0] or row < 0 or row >= self.board.shape[0]:
            return False
        return self.board[col, row] == 0

    def place_stone(self, col, row):
        player = 1 if self.black_turn else 2
        self.board[col, row] = player
        self.handle_captures()

    def handle_captures(self):
        self_color = "black" if self.black_turn else "white"
        other_color = "white" if self.black_turn else "black"
        captured_count = self.capture_stones(other_color)
        self.prisoners[self_color] += captured_count

    def capture_stones(self, color):
        color_code = 1 if color == "black" else 2
        captured_count = 0
        for group in list(get_stone_groups(self.board, color)):
            if has_no_liberties(self.board, group):
                for i, j in group:
                    self.board[i, j] = 0
                    captured_count += 1
        return captured_count

    def check_winner(self):
        if self.prisoners['black'] >= WINNING_SCORE:
            return "Black"
        elif self.prisoners['white'] >= WINNING_SCORE:
            return "White"
        return None

    def show_winner_message(self, winner):
        font = pygame.font.Font(None, 74)
        text = font.render(f"{winner} wins!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.fill((0, 0, 0))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    def draw(self):
        self.clear_screen()
        for col, row in zip(*np.where(self.board == 1)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, BLACK)
        for col, row in zip(*np.where(self.board == 2)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, WHITE)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, WHITE)

        font = pygame.font.Font(None, 36)
        black_score_text = font.render(f"Black: {self.prisoners['black']}", True, BLACK)
        white_score_text = font.render(f"White:{self.prisoners['white']}", True, WHITE)

        screen_width = self.screen.get_width()
        self.screen.blit(black_score_text, (50, 10))
        self.screen.blit(white_score_text, (screen_width - white_score_text.get_width() - 50, 10))
        pygame.display.flip()

    def update(self):
        """Логика автоматического совершения ходов ИИ."""
        if self.game_over:
            return

        pygame.time.wait(400)  # Задержка для комфортного восприятия игры человека

        # 1. Режим игры против Минимакса
        if self.game_mode == "ai_minimax":
            if self.minimax_agent is None:
                from rl.minimax import MinimaxAgent
                self.minimax_agent = MinimaxAgent(color="white", depth=1)

            from rl.environment import AtariGoEnv
            env_wrapper = AtariGoEnv(size=self.size)
            env_wrapper.game = self

            action_id = self.minimax_agent.choose_action(env_wrapper)
            if action_id is not None:
                col = action_id // self.size
                row = action_id % self.size
                self.place_stone(col, row)

        # 2. Режим игры против Q-learning агента
        elif self.game_mode == "ai_qa":
            if self.ai_agent is None:
                from rl.agent import QLearningAgent
                self.ai_agent = QLearningAgent()
                self.ai_agent.load_q_table("rl/data/q_table.pkl")

            state_str = "".join(map(str, self.board.flatten()))
            valid_actions = []
            for c in range(self.size):
                for r in range(self.size):
                    if self.is_valid_move(c, r):
                        valid_actions.append(c * self.size + r)

            action_id = self.ai_agent.choose_action(state_str, valid_actions, train=False)
            if action_id is not None:
                col = action_id // self.size
                row = action_id % self.size
                self.place_stone(col, row)

        if self.place_sound:
            self.place_sound.play()

        winner = self.check_winner()
        if winner:
            self.game_over = True
            self.show_winner_message(winner)
            return

        self.black_turn = True
        self.draw()

if __name__ == "__main__":
    # Для обучения и тестов лучше поставить размер доски 9, чтобы алгоритмы работали быстрее.
    # Но этот код полностью поддерживает любой размер, например 9x9 или 18x18.
    g = Game(size=9)
    g.start()