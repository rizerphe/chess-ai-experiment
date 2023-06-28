import chess
import chess.pgn
import yaml

path = "./lichess_2022_02.pgn"

pgn = open(path)
higher_rated_offsets = []

count = 0
while True:
    offset = pgn.tell()
    headers = chess.pgn.read_headers(pgn)
    if headers is None or count > 20000:
        break
    elos = headers.get("WhiteElo"), headers.get("BlackElo")
    if any(not i.isnumeric() or int(i) < 1600 for i in elos):
        continue
    higher_rated_offsets.append(offset)
    count += 1

moves = {}

count = 0
for offset in higher_rated_offsets:
    pgn.seek(offset)
    game = chess.pgn.read_game(pgn)
    if count > 20000:
        break
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


with open("lichess_2022_02.yaml", "w") as f:
    yaml.dump(moves, f)
