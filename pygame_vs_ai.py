import glob

import chess
import chess.pgn
import pygame

from amplify import amplified_predictor
from predict import Predictor
from pygame_interface import ChessGame


def main():
    cell_size = 64
    predictor = amplified_predictor(Predictor("network_9.pth"), 2)
    game = ChessGame(chess.Board(), cell_size)
    pygame.init()
    screen = pygame.display.set_mode((8 * cell_size, 8 * cell_size))
    pygame.display.set_caption("Chess")
    running = True
    while running:
        if game.board.is_game_over():
            print("Game over")
            break
        ai_turn = game.board.turn == chess.BLACK
        if ai_turn:
            running = game.iteration(screen, False)
            moves = predictor(game.board)
            top_move = max(moves, key=lambda move: moves[move])
            game.board.push(top_move)
        else:
            running = game.iteration(screen, True)

    pygame.quit()

    pgn = chess.pgn.Game.from_board(game.board)
    pgn.headers["Event"] = "Chess AI vs Human"
    pgn.headers["White"] = "Human"
    pgn.headers["Black"] = "AI"
    pgn.headers["Result"] = game.board.result()

    existing_files = glob.glob("logs/*.pgn")
    i = 1
    while f"logs/game_human_vs_ai{i}.pgn" in existing_files:
        i += 1
    with open(f"logs/game_human_vs_ai{i}.pgn", "w", encoding="utf-8") as f:
        f.write(str(pgn))
        print(f"Game saved as game_human_vs_ai{i}.pgn")


if __name__ == "__main__":
    main()
