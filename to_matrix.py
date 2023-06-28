from dataclasses import dataclass
import random
from typing import Iterator

import chess
import numpy as np
import yaml


@dataclass
class Strategy:
    board_and_move: np.ndarray
    rating: float


def board_and_move_to_matrix(board: chess.Board, move: chess.Move) -> np.ndarray:
    pieces = [
        "P",
        "N",
        "B",
        "R",
        "Q",
        "K",
    ]
    matrix = np.zeros((len(pieces) * 2 + 2, 8, 8), dtype=int)
    for square, piece in board.piece_map().items():
        matrix[
            (len(pieces) if piece.color else 0) + pieces.index(piece.symbol().upper()),
            square // 8,
            square % 8,
        ] = 1
    matrix[-1, move.from_square // 8, move.from_square % 8] = 1
    matrix[-2, move.to_square // 8, move.to_square % 8] = 1
    return matrix


def strategies_from_fen(fen: str, moves: list[str]) -> list[Strategy]:
    move_ratings = {move: moves.count(move) / len(moves) for move in set(moves)}
    board = chess.Board(fen)
    legal_moves = list(board.legal_moves)
    random.shuffle(legal_moves)
    non_human_moves = 0
    strategies = []
    for move in legal_moves:
        move_san = board.san(move)
        if move_san in move_ratings:
            strategies.append(
                Strategy(board_and_move_to_matrix(board, move), move_ratings[move_san])
            )
        else:
            if non_human_moves < len(moves):
                non_human_moves += 1
                strategies.append(Strategy(board_and_move_to_matrix(board, move), 0))
    return strategies


def strategies_from_file(path: str, n: int | None = 1000) -> Iterator[Strategy]:
    with open(path, "r") as file:
        data = yaml.safe_load(file)
    for i, (fen, moves) in enumerate(data.items()):
        sff = strategies_from_fen(fen, moves)
        if not i % 100:
            print(f"Loaded {len(sff)} strategies from {i + 1}st FEN")
            print(f"{sum(s.rating for s in sff) / len(sff)} average rating")
        if n and i > n:
            break
        yield from sff
