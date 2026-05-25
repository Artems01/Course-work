import pygame
import sys

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