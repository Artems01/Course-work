import os
import sys

# Добавляем корневую директорию проекта в пути поиска модулей, чтобы импорты работали корректно
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl.environment import AtariGoEnv
from rl.agent import QLearningAgent
from rl.minimax import MinimaxAgent

def train_agent(episodes=2000, board_size=9):
    """Фоновое обучение Q-learning агента в режиме Self-Play."""
    print(f"=== Запуск обучения агента ({episodes} эпизодов, доска {board_size}x{board_size}) ===")

    env = AtariGoEnv(size=board_size)
    agent = QLearningAgent(alpha=0.2, gamma=0.9, epsilon=0.4, epsilon_decay=0.9998)

    for episode in range(1, episodes + 1):
        state = env.reset()
        done = False

        last_state = None
        last_action = None

        while not done:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break

            action = agent.choose_action(state, valid_actions, train=True)
            next_state, reward, done, info = env.step(action)

            if last_state is not None and last_action is not None:
                agent.learn(last_state, last_action, -reward, next_state, valid_actions, done)

            next_valid = env.get_valid_actions() if not done else []
            agent.learn(state, action, reward, next_state, next_valid, done)

            last_state = state
            last_action = action
            state = next_state

        agent.decay_epsilon()

        if episode % 500 == 0:
            print(f"Эпизод {episode}/{episodes} завершен. Текущий Epsilon: {agent.epsilon:.4f}")

    os.makedirs("rl/data", exist_ok=True)
    agent.save_q_table("rl/data/q_table.pkl")
    print("=== Обучение успешно завершено и модель сохранена! ===\n")
    return agent

def evaluate_agent(agent, test_episodes=100, board_size=9):
    """Тестирование обученного Q-агента против Минимакса."""
    print(f"=== Запуск тестирования: Обученный Агент (Черные) vs Minimax (Белые) ===")

    env = AtariGoEnv(size=board_size)
    minimax_opponent = MinimaxAgent(color="white", depth=1)

    agent_wins = 0
    minimax_wins = 0
    draws = 0

    for episode in range(1, test_episodes + 1):
        env.reset()
        done = False

        while not done:
            # Ход Черных (Наш Q-learning Агент)
            if env.game.black_turn:
                state_str = env._get_state_string()
                valid_actions = env.get_valid_actions()
                if not valid_actions:
                    break
                action = agent.choose_action(state_str, valid_actions, train=False)
                if action is not None:
                    _, _, done, info = env.step(action)
                else:
                    break

            # Ход Белых (Минимакс)
            else:
                action = minimax_opponent.choose_action(env)
                if action is not None:
                    _, _, done, info = env.step(action)
                else:
                    break

        # Проверка победителя партии
        winner = env.game.check_winner()
        if winner == "Black":
            agent_wins += 1
        elif winner == "White":
            minimax_wins += 1
        else:
            draws += 1

    print("=========================================================================")
    print(f"{'Режим партии':<35} | {'Победы Агента':<13} | {'Победы Minimax':<14} | {'Ничьи'}")
    print("-------------------------------------------------------------------------")
    print(f"{'Обученный агент vs Minimax':<35} | {agent_wins:<13} | {minimax_wins:<14} | {draws}")
    print("=========================================================================")

if __name__ == "__main__":
    trained_agent = train_agent(episodes=2000, board_size=9)
    evaluate_agent(trained_agent, test_episodes=100, board_size=9)