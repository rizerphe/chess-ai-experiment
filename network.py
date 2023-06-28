import matplotlib.pyplot as plt
import torch

import to_matrix


class Thinker(torch.nn.Module):
    def __init__(self, size: int):
        super().__init__()
        self.thinker = torch.nn.Linear(size, size)

    def forward(self, x):
        return x + self.thinker(x)


class Network(torch.nn.Module):
    def __init__(self, n_filters=8, n_hidden=0, thinker_size=16, n_thinkers=0):
        super().__init__()
        self.chess_move_quality_predictor = torch.nn.Sequential(
            torch.nn.Conv2d(14, 16, 4, padding=2),
            torch.nn.ReLU(),
            torch.nn.Conv2d(16, 16, 4, padding=2, stride=2),
            torch.nn.ReLU(),
            torch.nn.Conv2d(16, n_filters, 4, padding=2),
            torch.nn.ReLU(),
            *[
                torch.nn.Sequential(
                    torch.nn.Conv2d(n_filters, n_filters, 4, padding="same"),
                    torch.nn.ReLU(),
                )
                for _ in range(n_hidden)
            ],
            torch.nn.Conv2d(n_filters, 6, 2),
            torch.nn.ReLU(),
            torch.nn.Flatten(),
            torch.nn.Linear(150, thinker_size),
            torch.nn.ReLU(),
            *[Thinker(thinker_size) for _ in range(n_thinkers)],
            torch.nn.Linear(thinker_size, 8),
            torch.nn.Sigmoid(),
            torch.nn.Linear(8, 2),
            torch.nn.Sigmoid(),
            torch.nn.Softmax(dim=1),
        )

    def forward(self, x):
        return self.chess_move_quality_predictor(x)


def train():
    dataset = to_matrix.strategies_from_file("fens.yaml", 200000)
    network = Network()
    optimizer = torch.optim.Adam(network.parameters(), lr=0.01)
    print(f"Num params: {sum(p.numel() for p in network.parameters())}")
    loss_function = torch.nn.MSELoss()
    all_moves = list(dataset)
    print(f"Loaded {len(all_moves)} moves")
    all_board_and_moves = torch.Tensor(
        [strategy.board_and_move for strategy in all_moves]
    )
    all_ratings = torch.Tensor([[move.rating, 1 - move.rating] for move in all_moves])
    losses = []
    for epoch in range(1000):
        optimizer.zero_grad()
        output = network(all_board_and_moves)
        loss = loss_function(output, all_ratings)
        print(
            f"Loss: {loss} after epoch {epoch}; example output: {output[0]}, target: {all_ratings[0]}"
        )
        losses.append(loss.item())
        loss.backward()
        optimizer.step()

        if not epoch % 100:
            torch.save(network.state_dict(), f"network_3_epoch_{epoch}.pt")
            plt.plot(losses)
            plt.show()


if __name__ == "__main__":
    train()
