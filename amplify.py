from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Callable

import chess


@dataclass
class Scenario:
    board: chess.Board
    move: chess.Move | None
    score: float
    predict: Callable[[chess.Board], dict[chess.Move, float]]
    explored_children: list[Scenario] | None = None
    depth_coef: float = 1.25
    rewarded_move_number: float = 24
    score_override_coef: float = 0.1

    def expand(self) -> bool:
        if self.explored_children is not None:
            child_to_expand = max(
                self.explored_children,
                key=lambda child: child.expansion_probability(),
            )
            return child_to_expand.expand()

        # if trying to expand a game over scenario, return False
        if self.board.is_game_over():
            return False

        self.explored_children = []
        for move, score in self.predict(self.board).items():
            board = self.board.copy()
            board.push(move)
            self.explored_children.append(
                Scenario(
                    board=board,
                    move=move,
                    score=score,
                    predict=self.predict,
                )
            )
        return True

    def expansion_probability(self):
        # Special treatment for game over scenarios
        if self.board.is_game_over():
            return 0
        if self.explored_children is None:
            return self.score
        return (
            sum(
                child.expansion_probability() ** 2 / self.depth_coef
                for child in self.explored_children
            )
            / len(self.explored_children)
        ) ** 0.5

    def move_numbers_price(self, moves: int):
        sigmoid_value = math.exp(moves / self.rewarded_move_number) / (
            1 + math.exp(moves / self.rewarded_move_number)
        )
        return sigmoid_value * 2 - 1

    def value(self):
        # Special treatment for game over scenarios
        if self.board.is_game_over():
            # We return 1 for a win, 0 for a loss, and 0.5 for a draw
            return (
                1
                if self.board.result() == "1-0"
                else (0 if self.board.result() == "0-1" else 0.5)
            )
        if self.explored_children is None:
            return self.score
        return (
            (1 - max(child.value() for child in self.explored_children))
            ** (1 - self.score_override_coef)
            * (self.score**self.score_override_coef)
            * self.move_numbers_price(self.board.fullmove_number)
        )

    def n_explored(self):
        if self.explored_children is None:
            return 1
        return sum(child.n_explored() for child in self.explored_children)

    def depth(self):
        if self.explored_children is None:
            return 0
        return 1 + max(child.depth() for child in self.explored_children)


def amplify(
    board, predict: Callable[[chess.Board], dict[chess.Move, float]], n_scenarios: int
) -> dict[chess.Move, float]:
    scenario = Scenario(board=board, move=None, score=0, predict=predict)
    while scenario.n_explored() < n_scenarios and scenario.expand():
        pass
    return {
        child.move: child.value()
        for child in scenario.explored_children or []
        if child.move
    }


def amplified_predictor(predict, n):
    def predictor(b):
        return amplify(b, predict, n)

    return predictor
