from typing import Tuple

from coliseum.game.game_layout.board import Board, Piece


class BoardTictac(Board):
    """
    Attributes:
        env: environnement dictionnary (composed of pieces)
        dimensions: dimensions of the board
    """

    def __init__(self, env: dict[Tuple[int], Piece], dim: list[int]) -> None:
        super().__init__(env, dim)

    def __str__(self) -> str:
        return super().__str__()

    def to_json(self) -> dict:
        board = [[None for _ in range(self.dimensions[1])] for _ in range(self.dimensions[0])]
        for key, value in self.env.items():
            board[key[0]][key[1]] = value.piece_type if value is not None else None
        return {"board": board}
