import glob

import chess
import chess.pgn

from amplify import amplify
from predict import predict


def rerank_with_repetition(b, moves):
    for move in moves:
        b.push(move)
        for i in range(6, 0, -1):
            if b.is_repetition(i):
                moves[move] /= i + 1
                break
        b.pop()
    return moves


def play():
    # An AI vs AI game
    b = chess.Board()
    try:
        while (
            not b.is_checkmate()
            and not b.is_stalemate()
            and not b.is_insufficient_material()
        ):
            print(b)
            print()
            moves = rerank_with_repetition(b, amplify(b, predict, 1000))
            for move, _rating in sorted(
                moves.items(), key=lambda x: x[1], reverse=True
            ):
                b.push(move)
                if b.is_repetition(7):
                    b.pop()
                    continue
                break
            else:
                print("No more non-repeating moves")
                break
    except KeyboardInterrupt:
        pass

    # Save game history as pgn
    pgn = chess.pgn.Game.from_board(b)
    existing_files = glob.glob("logs/*.pgn")
    i = 1
    while f"logs/game{i}.pgn" in existing_files:
        i += 1
    with open(f"logs/game{i}.pgn", "w") as f:
        f.write(str(pgn))
        print(f"Game saved as game{i}.pgn")


if __name__ == "__main__":
    play()
