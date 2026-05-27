import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from rl.environment import AtariGoEnv
from rl.agent import QLearningAgent
from rl.minimax import MinimaxAgent

def train_agent(
        episodes=300,
        board_size=5
):

    env = AtariGoEnv(size=board_size)

    agent = QLearningAgent(
        alpha=0.2,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        min_epsilon=0.05
    )

    minimax_opponent = MinimaxAgent(
        color='white',
        depth=1
    )

    for episode in range(episodes):

        state = env.reset()

        done = False

        move_limit = 0

        while not done:

            move_limit += 1

            # защита от бесконечной игры
            if move_limit > 100:
                break

            # ===== ХОД Q-LEARNING =====
            if env.game.black_turn:

                valid_actions = env.get_valid_actions()

                if not valid_actions:
                    break

                action = agent.choose_action(
                    state,
                    valid_actions,
                    train=True
                )

                next_state, reward, done, _ = env.step(action)

                next_actions = env.get_valid_actions()

                agent.learn(
                    state,
                    action,
                    reward,
                    next_state,
                    next_actions,
                    done
                )

                state = next_state

            # ===== ХОД MINIMAX =====
            else:

                action = minimax_opponent.choose_action(env)

                if action is None:
                    break

                next_state, reward, done, _ = env.step(action)

                state = next_state

        agent.decay_epsilon()

        if episode % 50 == 0:

            print(
                f'Episode {episode} | epsilon={agent.epsilon:.3f}'
            )

    # СОХРАНЕНИЕ Q-TABLE
    os.makedirs('data', exist_ok=True)

    agent.save_q_table(
        'data/q_table.pkl'
    )

    print('\nОбучение завершено.')

    return agent

def evaluate_agent(
        agent,
        test_episodes=20,
        board_size=5
):

    print(
        '\n=== ТЕСТ: AGENT VS MINIMAX ===\n'
    )

    env = AtariGoEnv(size=board_size)

    minimax_opponent = MinimaxAgent(
        color='white',
        depth=1
    )

    agent_wins = 0
    minimax_wins = 0
    draws = 0

    for episode in range(test_episodes):

        state = env.reset()

        done = False

        move_limit = 0

        while not done:

            move_limit += 1

            if move_limit > 100:
                draws += 1
                break

            # ===== AGENT =====
            if env.game.black_turn:

                valid_actions = env.get_valid_actions()

                if not valid_actions:
                    draws += 1
                    break

                action = agent.choose_action(
                    state,
                    valid_actions,
                    train=False
                )

                if action is None:
                    draws += 1
                    break

                next_state, reward, done, _ = env.step(action)

                state = next_state

            # ===== MINIMAX =====
            else:

                action = minimax_opponent.choose_action(env)

                if action is None:
                    draws += 1
                    break

                next_state, reward, done, _ = env.step(action)

                state = next_state

        winner = env.game.check_winner()

        if winner == "Black":

            agent_wins += 1

        elif winner == "White":

            minimax_wins += 1

        else:

            draws += 1
        print("==========================================")
        print(f"Победы агента   : {agent_wins}")
        print(f"Победы minimax  : {minimax_wins}")
        print(f"Ничьи           : {draws}")
        print("==========================================")


if __name__ == "__main__":
    trained_agent = train_agent(
        episodes=300,
        board_size=5
    )

    evaluate_agent(
        trained_agent,
        test_episodes=20,
        board_size=5
    )