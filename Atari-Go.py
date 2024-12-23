import pygame
import numpy as np
import itertools
import sys
import networkx as nx
import collections
from pygame import gfxdraw



# Game constants
BOARD_BROWN = (194, 105, 42)
BOARD_WIDTH = 1010
BOARD_BORDER = 75
STONE_RADIUS = 22
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TURN_POS = (BOARD_BORDER, 20)
SCORE_POS = (BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER + 30)
DOT_RADIUS = 4
WINNING_SCORE = 1


def make_grid(size):
    """Return list of (start_point, end_point pairs) defining gridlines
    Args:
        size (int): size of grid
    Returns:
        Tuple[List[Tuple[float, float]]]: start and end points for gridlines
    """
    start_points, end_points = [], []

    # vertical start points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_BORDER)
    start_points += list(zip(xs, ys))

    # horizontal start points (constant x)
    xs = np.full((size), BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    start_points += list(zip(xs, ys))

    # vertical end points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    end_points += list(zip(xs, ys))

    # horizontal end points (constant x)
    xs = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    end_points += list(zip(xs, ys))

    return (start_points, end_points)


def xy_to_colrow(x, y, size):
    """Convert x,y coordinates to column and row number
    Args:
        x (float): x position
        y (float): y position
        size (int): size of grid
    Returns:
        Tuple[int, int]: column and row numbers of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x_dist = x - BOARD_BORDER
    y_dist = y - BOARD_BORDER
    col = int(round(x_dist / inc))
    row = int(round(y_dist / inc))
    return col, row


def colrow_to_xy(col, row, size):
    """Convert column and row numbers to x,y coordinates
    Args:
        col (int): column number (horizontal position)
        row (int): row number (vertical position)
        size (int): size of grid
    Returns:
        Tuple[float, float]: x,y coordinates of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x = int(BOARD_BORDER + col * inc)
    y = int(BOARD_BORDER + row * inc)
    return x, y


def has_no_liberties(board, group):
    """Check if a stone group has any liberties on a given board.
    Args:
        board (object): game board (size * size matrix)
        group (List[Tuple[int, int]]): list of (col,row) pairs defining a stone group
    Returns:
        [boolean]: True if group has any liberties, False otherwise
    """
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
    """Get stone groups of a given color on a given board
    Args:
        board (object): game board (size * size matrix)
        color (str): name of color to get groups for
    Returns:
        List[List[Tuple[int, int]]]: list of list of (col, row) pairs, each defining a group
    """
    size = board.shape[0]
    color_code = 1 if color == "black" else 2
    xs, ys = np.where(board == color_code)
    graph = nx.grid_graph(dim=[size, size])
    stones = set(zip(xs, ys))
    all_spaces = set(itertools.product(range(size), range(size)))
    stones_to_remove = all_spaces - stones
    graph.remove_nodes_from(stones_to_remove)
    return nx.connected_components(graph)


def is_valid_move(col, row, board):
    """Check if placing a stone at (col, row) is valid on board
    Args:
        col (int): column number
        row (int): row number
        board (object): board grid (size * size matrix)
    Returns:
        boolean: True if move is valid, False otherewise
    """
    # TODO: check for ko situation (infinite back and forth)
    if col < 0 or col >= board.shape[0]:
        return False
    if row < 0 or row >= board.shape[0]:
        return False
    return board[col, row] == 0

def draw_menu(screen, font):
    """Draws the main menu on the screen."""
    screen.fill((0, 0, 0))  # Black background

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    button_width_ratio = 0.4
    button_height_ratio = 0.1
    button_padding_ratio = 0.1

    button_width = int(screen_width * button_width_ratio)
    button_height = int(screen_height * button_height_ratio)
    button_padding = int(screen_height * button_padding_ratio)
    button_color = (100, 100, 255)
    text_color = (255, 255, 255)

    # Play button
    play_button_y = (screen_height - 3 * button_height - 2 * button_padding) // 2 + button_height
    play_button_rect = pygame.Rect((screen_width - button_width) // 2, play_button_y, button_width, button_height)
    pygame.draw.rect(screen, button_color, play_button_rect)
    play_text = font.render("Играть без регистрации", True, text_color)
    play_text_rect = play_text.get_rect(center=play_button_rect.center)
    screen.blit(play_text, play_text_rect)

    # Register button
    register_button_y = play_button_y + button_height + button_padding
    register_button_rect = pygame.Rect((screen_width - button_width) // 2, register_button_y, button_width, button_height)
    pygame.draw.rect(screen, button_color, register_button_rect)
    register_text = font.render("Зарегистрироваться", True, text_color)
    register_text_rect = register_text.get_rect(center=register_button_rect.center)
    screen.blit(register_text, register_text_rect)

    # Rules button
    rules_button_y = register_button_y + button_height + button_padding
    rules_button_rect = pygame.Rect((screen_width - button_width) // 2, rules_button_y, button_width, button_height)
    pygame.draw.rect(screen, button_color, rules_button_rect)
    rules_text = font.render("Правила игры", True, text_color)
    rules_text_rect = rules_text.get_rect(center=rules_button_rect.center)
    screen.blit(rules_text, rules_text_rect)

    pygame.display.flip()
    return play_button_rect, register_button_rect, rules_button_rect

def handle_menu_click(pos, play_button_rect, register_button_rect, rules_button_rect):
    if play_button_rect.collidepoint(pos):
        return "play"
    elif register_button_rect.collidepoint(pos):
        return "register"
    elif rules_button_rect.collidepoint(pos):
        return "rules"
    else:
        return None

def show_rules(screen):
    """Displays the game rules on the screen."""
    screen.fill((255, 255, 255))  # White background
    font = pygame.font.Font(None, 28)

    rules = [
        "Правила игры:",
        "• Игра проводится на доске размера 18x18;",
        "• Ходы выполняются по очереди;",
        "• Играют два игрока: один использует черные фишки, другой — белые.",
        "• Игроки поочередно ставят свои фишки на пересечения линий на доске.",
        "• Фишка или группа фишек противника, которые вы окружили своими фишками, снимается с доски.",
        "• Побеждает игрок, первым окружившим один или несколько фишек противника."
    ]

    for i, line in enumerate(rules):
        text = font.render(line, True, (0, 0, 0))  # Black text
        screen.blit(text, (20, 20 + i * 30))

    # Кнопка "Главное меню"
    back_button_rect = pygame.Rect(20, 20 + len(rules) * 30 + 30, 200, 40)
    pygame.draw.rect(screen, (100, 100, 255), back_button_rect)  # Button color
    back_text = font.render("Главное меню", True, (255, 255, 255))  # White text
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)

    pygame.display.flip()

    # Wait for user to return to menu
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if back_button_rect.collidepoint(event.pos):  # Check if back button is clicked
                    waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to return
                    waiting = False

def registration(game):  # Pass Game instance
    reg_screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Регистрация")
    font = pygame.font.Font(None, 32)
    username = ''
    password = ''
    input_active = [True, False]  # [username_input_active, password_input_active]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Вернуться в главное меню, если окно закрыто
            if event.type == pygame.KEYDOWN:
                if input_active[0]:  # Ввод никнейма
                    if event.key == pygame.K_RETURN:
                        input_active[0] = False
                        input_active[1] = True
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode

                elif input_active[1]:  # Ввод пароля
                    if event.key == pygame.K_RETURN:
                        if username and password:  # Проверка на пустые поля
                            show_success_message(game)
                            running = False  # Выход из цикла после успешной регистрации
                    elif event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        password += event.unicode

        reg_screen.fill((255, 255, 255))  # White background
        username_text = font.render('Введите никнейм:', True, (0, 0, 0))  # Black text
        password_text = font.render('Введите пароль:', True, (0, 0, 0))

        reg_screen.blit(username_text, (20, 20))
        reg_screen.blit(font.render(username, True, (0, 0, 0)), (20, 60))

        reg_screen.blit(password_text, (20, 120))
        reg_screen.blit(font.render('*' * len(password), True, (0, 0, 0)), (20, 160))
        pygame.display.flip()

    pygame.display.quit()  # Quit ONLY the registration display
    return True


def show_success_message(game):
    """Показывает сообщение об успешной регистрации и кнопку ОК."""
    success_screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Успех")
    font = pygame.font.Font(None, 36)
    text = font.render("Регистрация прошла успешно", True, (0, 0, 0))
    ok_button_rect = pygame.Rect(150, 120, 100, 40)  # Кнопка ОК

    while True:
        success_screen.fill(WHITE)
        text_rect = text.get_rect(center=(200, 100))
        success_screen.blit(text, text_rect)

        # Рисуем кнопку ОК
        pygame.draw.rect(success_screen, (100, 100, 255), ok_button_rect)
        ok_text = font.render("ОК", True, (255, 255, 255))
        ok_text_rect = ok_text.get_rect(center=ok_button_rect.center)
        success_screen.blit(ok_text, ok_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if ok_button_rect.collidepoint(event.pos):
                    return  # Возврат к игровому процессу

def show_registration_error():
    """Показывает экран с ошибкой, если не введены данные."""
    error_screen = pygame.display.set_mode((1010, 1010))
    pygame.display.set_caption("Ошибка")
    font = pygame.font.Font(None, 32)
    text = font.render("Введите никнейм и пароль", True, (0, 0, 0))
    ok_button_rect = pygame.Rect(465, 510, 70, 30)  # Кнопка ОК

    while True:
        error_screen.fill(WHITE)
        text_rect = text.get_rect(center=(500, 500))
        error_screen.blit(text, text_rect)

        # Рисуем кнопку ОК
        pygame.draw.rect(error_screen, (100, 100, 255), ok_button_rect)
        ok_text = font.render("ОК", True, (255, 255, 255))
        ok_text_rect = ok_text.get_rect(center=ok_button_rect.center)
        error_screen.blit(ok_text, ok_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if ok_button_rect.collidepoint(event.pos):
                    return  # Возврат к регистрации

class Game:
    def __init__(self, size):
        self.board = np.zeros((size, size))
        self.size = size
        self.black_turn = True
        self.prisoners = collections.defaultdict(int)
        self.start_points, self.end_points = make_grid(self.size)

    def start(self):
        self.init_pygame()
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("arial", 36)

        while True:
            play_button_rect, register_button_rect, rules_button_rect = draw_menu(self.screen, font)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    action = handle_menu_click(event.pos, play_button_rect, register_button_rect, rules_button_rect)
                    if action == "play":
                        self.play_game()
                        return
                    elif action == "register":
                        if not registration(self):  # Pass game instance
                            show_registration_error()  # Показать ошибку, если регистрация была закрыта
                            continue
                        self.play_game()
                        return
                    elif action == "rules":
                        show_rules(self.screen)  # Show game rules

            clock.tick(30)

    def play_game(self, fullscreen=False):
        if fullscreen:
            self.init_pygame(fullscreen=True)
        else:
            self.init_pygame()

        self.clear_screen()
        self.draw()
        while True:
            self.update()
            pygame.time.wait(100)


    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 30)
        self.place_sound = pygame.mixer.Sound("move_fishki.wav")
        pygame.mixer.init()  # Инициализация модуля микширования

    def clear_screen(self):

        # fill board and add gridlines
        self.screen.fill(BOARD_BROWN)
        for start_point, end_point in zip(self.start_points, self.end_points):
            pygame.draw.line(self.screen, BLACK, start_point, end_point)

        # add guide dots
        guide_dots = [3, self.size // 2, self.size - 4]
        for col, row in itertools.product(guide_dots, guide_dots):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, DOT_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, DOT_RADIUS, BLACK)

        pygame.display.flip()

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


    def draw(self):
        self.clear_screen()  # Clear the screen for redrawing

        # Draw stones
        for col, row in zip(*np.where(self.board == 1)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, BLACK)
        for col, row in zip(*np.where(self.board == 2)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, WHITE)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, WHITE)


        # Display scores at the top
        font = pygame.font.Font(None, 36)  # Choose a suitable font and size
        black_score_text = font.render(f"Black: {self.prisoners['black']}", True, BLACK)
        white_score_text = font.render(f"White: {self.prisoners['white']}", True, WHITE)

        # Position the score text near the top of the screen. Adjust these values as needed
        screen_width = self.screen.get_width()
        black_score_x = 50  # Adjust x-coordinate as needed
        white_score_x = screen_width - white_score_text.get_width() - 50  # Right-align White score


        self.screen.blit(black_score_text, (black_score_x, 10))  # Adjust y-coordinate as needed
        self.screen.blit(white_score_text, (white_score_x, 10))  # Adjust y-coordinate as needed

        pygame.display.flip()

    def update(self):
        # TODO: undo button
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                self.handle_click()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    self.pass_move()


if __name__ == "__main__":
    g = Game(size=19)
    g.init_pygame()
    g.clear_screen()
    g.draw()
    g.start()

    while True:
        g.update()
        pygame.time.wait(100)