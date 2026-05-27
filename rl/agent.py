import os
import pickle
import random

class QLearningAgent:

    def __init__(
        self,
        alpha=0.2,
        gamma=0.9,
        epsilon=0.3,
        epsilon_decay=0.9995,
        min_epsilon=0.01,
    ):
        """Реализация Q-learning агента для Atari-Go.

        Args:
            alpha (float): Скорость обучения (learning rate).
            gamma (float): Коэффициент дисконтирования (discount factor).
            epsilon (float): Вероятность случайного хода (exploration rate).
            epsilon_decay (float): Коэффициент затухания epsilon после каждого
            шага/эпизода. min_epsilon (float): Минимальное значение epsilon.
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

        # Q-таблица: {(state_str, action_id): q_value}
        self.q_table = {}

    def get_q_value(self, state, action):
        """Возвращает Q-значение для пары (состояние, действие).

        Если пары нет в таблице, возвращает 0.0.
        """
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, valid_actions, train=True):
        """Выбирает действие на основе epsilon-greedy стратегии.

        Args:
            state (str): Текущее состояние доски (строка).
            valid_actions (list): Список доступных action_id.
            train (bool): Если False, агент выбирает строго лучшее действие (режим
              игры).
        """
        if not valid_actions:
            return None

        # Эпсилон-жадный выбор в режиме обучения
        if train and random.random() < self.epsilon:
            return random.choice(valid_actions)

        # Выбираем лучшее действие из доступных (жадная стратегия)
        max_q = float("-inf")
        best_actions = []

        for action in valid_actions:
            q_val = self.get_q_value(state, action)
            if q_val > max_q:
                max_q = q_val
                best_actions = [action]
            elif q_val == max_q:
                best_actions.append(action)

        # Если несколько ходов имеют одинаковую максимальную оценку, выбираем случайно среди них
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state, next_valid_actions, done):
        """Обновление Q-значения по формуле:

        Q(s,a) := Q(s,a) + alpha * (r + gamma * max_a' Q(s',a') - Q(s,a))
        """
        current_q = self.get_q_value(state, action)

        # Находим максимум Q-функции для следующего состояния
        if done or not next_valid_actions:
            max_future_q = 0.0
        else:
            max_future_q = max(
                [self.get_q_value(next_state, a) for a in next_valid_actions]
            )

        # Формула Q-обучения
        new_q = current_q + self.alpha * (
            reward + self.gamma * max_future_q - current_q
        )
        self.q_table[(state, action)] = new_q

    def decay_epsilon(self):
        """Уменьшает epsilon для снижения случайных ходов по ходу обучения."""
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay
            if self.epsilon < self.min_epsilon:
                self.epsilon = self.min_epsilon

    def save_q_table(self, filepath):
        """Сериализация Q-таблицы на диск."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(self.q_table, f)
        print(f"Q-таблица успешно сохранена в {filepath}")

    def load_q_table(self, filepath):
        """Загрузка Q-таблицы с диска."""
        import os
        import pickle

        if os.path.exists(filepath):
            # Проверяем, что файл не пустой (размер больше 0 байт)
            if os.path.getsize(filepath) > 0:
                try:
                    with open(filepath, "rb") as f:
                        self.q_table = pickle.load(f)
                    print(f"Q-таблица успешно загружена из {filepath}")
                except Exception as e:
                    print(
                        f"Ошибка при чтении Q-таблицы: {e}. Начинаем с пустой"
                        " таблицы."
                    )
                    self.q_table = {}
            else:
                print(
                    f"Файл {filepath} пустой. Агент начинает с пустой"
                    " Q-таблицей."
                )
                self.q_table = {}
        else:
            print(
                f"Файл {filepath} не найден. Агент начинает с пустой"
                " Q-таблицей."
            )
            self.q_table = {}