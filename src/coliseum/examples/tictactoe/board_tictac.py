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
