import chess
import chess.pgn
import click

from amplify import amplified_predictor
from predict import Predictor


def play_against_ai(checkpoint: str):
    board = chess.Board()
    w_predictor = Predictor(checkpoint)
    predictor = amplified_predictor(w_predictor, 1000)
    while not board.is_game_over():
        if board.turn == chess.WHITE:
            print(board)
            while True:
                try:
                    move = input("Enter your move: ")
                    board.push_san(move)
                    break
                except ValueError:
                    print("Invalid move")
        else:
            moves = predictor(board)
            move = max(moves, key=lambda x: moves[x])
            print("AI move: ", move)
            board.push(move)
    print(board.result())
    print()

    # Save pgn
    pgn = chess.pgn.Game.from_board(board)
    pgn.headers["Event"] = "AI vs Human"
    pgn.headers["White"] = "Human"
    pgn.headers["Black"] = "AI"
    pgn.headers["Result"] = board.result()
    with open("ai_vs_human.pgn", "w") as f:
        f.write(str(pgn))


@click.command()
@click.option("--checkpoint", default="network_9.pth")
def main(checkpoint: str):
    play_against_ai(checkpoint)


if __name__ == "__main__":
    main()
