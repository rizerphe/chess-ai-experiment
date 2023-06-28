import chess
import pygame


class ChessGame:
    def __init__(self, board: chess.Board, cell_size: int = 100):
        self.board = board
        self.cell_size = cell_size
        self.starting_position = None

    def draw_board(self, screen):
        # Draw the board
        for row in range(8):
            for column in range(8):
                if (row + column) % 2 == 0:
                    pygame.draw.rect(
                        screen,
                        (255, 255, 255),
                        (
                            row * self.cell_size,
                            column * self.cell_size,
                            self.cell_size,
                            self.cell_size,
                        ),
                    )
                else:
                    pygame.draw.rect(
                        screen,
                        (31, 63, 127),
                        (
                            row * self.cell_size,
                            column * self.cell_size,
                            self.cell_size,
                            self.cell_size,
                        ),
                    )

    def draw_pieces(self, screen):
        # Draw the pieces
        for row in range(8):
            for column in range(8):
                piece = self.board.piece_at(chess.square(row, column))
                if piece is not None:
                    screen.blit(
                        pygame.image.load(
                            f"assets/{piece.symbol()}.png"
                        ).convert_alpha(),
                        (row * self.cell_size, (7 - column) * self.cell_size),
                    )

    def draw_legal_moves(self, screen, starting_position):
        # Draw the legal moves
        for move in self.board.legal_moves:
            if move.from_square == starting_position:
                pygame.draw.rect(
                    screen,
                    (0, 255, 0),
                    (
                        chess.square_file(move.to_square) * self.cell_size,
                        (7 - chess.square_rank(move.to_square)) * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    ),
                )

    def draw(self, screen, starting_position=None):
        self.draw_board(screen)
        self.draw_pieces(screen)
        if starting_position is not None:
            self.draw_legal_moves(screen, starting_position)
        pygame.display.update()

    def iteration(self, screen, allow_actions):
        self.draw(screen, self.starting_position)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif (
                allow_actions
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.starting_position = chess.square(
                    event.pos[0] // self.cell_size, 7 - event.pos[1] // self.cell_size
                )
            elif (
                allow_actions
                and event.type == pygame.MOUSEBUTTONUP
                and event.button == 1
            ):
                ending_position = chess.square(
                    event.pos[0] // self.cell_size, 7 - event.pos[1] // self.cell_size
                )
                if self.starting_position is None:
                    continue
                # Detect promotions:
                if self.board.piece_type_at(
                    self.starting_position
                ) == chess.PAWN and chess.square_rank(ending_position) in [0, 7]:
                    move = chess.Move(
                        self.starting_position,
                        ending_position,
                        promotion=chess.QUEEN,
                    )
                else:
                    move = chess.Move(self.starting_position, ending_position)
                if move in self.board.legal_moves:
                    self.board.push(move)
                self.starting_position = None
        return True


def main():
    cell_size = 64
    game = ChessGame(chess.Board(), cell_size)
    pygame.init()
    screen = pygame.display.set_mode((8 * cell_size, 8 * cell_size))
    pygame.display.set_caption("Chess")
    while game.iteration(screen, True):
        pass


if __name__ == "__main__":
    main()
