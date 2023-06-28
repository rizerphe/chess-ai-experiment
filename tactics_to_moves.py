import chess
import chess.pgn
import yaml

path = "./tactics.pgn"

NUM_MOVES = 100000

pgn = open(path)
higher_rated_offsets = []

count = 0
while True:
    offset = pgn.tell()
    headers = chess.pgn.read_headers(pgn)
    if headers is None or count > NUM_MOVES:
        break
    higher_rated_offsets.append(offset)
    count += 1

moves = {}

count = 0
for offset in higher_rated_offsets:
    pgn.seek(offset)
    game = chess.pgn.read_game(pgn)
    if game.errors:
        continue
    board = game.board()
    prev_fen = board.fen(en_passant="fen")
    game = game.next()
    while game:
        board = game.board()
        fen = board.fen(en_passant="fen")
        move = str(game.san())
        if prev_fen in moves:
            moves[prev_fen].append(move)
        else:
            moves[prev_fen] = [move]
        prev_fen = fen
        game = game.next()
        count += 1


with open(f"tactics_{len(moves)}.yaml", "w") as f:
    yaml.dump(moves, f)
