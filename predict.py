import chess
import click
import torch

from network import Network
import to_matrix


class Predictor:
    def __init__(self, checkpoint: str = "network_9.pt", *network_params):
        self.network = Network(*network_params)  # 48, 3, 128, 2)
        self.network.load_state_dict(
            torch.load(checkpoint, map_location=torch.device("cpu"))
        )
        self.network.eval()

    def __call__(self, board) -> dict[chess.Move, float]:
        moves = []
        for move in board.legal_moves:
            matrix = to_matrix.board_and_move_to_matrix(board, move)
            moves.append(matrix)
        moves = torch.Tensor(moves)
        with torch.no_grad():
            ratings = self.network(moves).numpy()
        return {move: rating[0] for move, rating in zip(board.legal_moves, ratings)}


def Predictor_large(checkpoint):
    return Predictor(checkpoint, 48, 3, 128, 2)


@click.command()
@click.option("--checkpoint", default="network_9.pt")
def main(checkpoint: str):
    predictor = Predictor(checkpoint)
    while True:
        fen = input("Enter FEN: ")
        board = chess.Board(fen)
        ratings = predictor(board)
        for move, rating in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            print(move, rating)


if __name__ == "__main__":
    main()
