from __future__ import annotations

from typing import Tuple

from typing import TYPE_CHECKING

from coliseum.game.game_layout.board import Board, Piece

if TYPE_CHECKING:
    from coliseum.player.player import Player


class PieceAvalam(Piece):
    def __init__(self, piece_type: str, owner: Player, value: int) -> None:
        super().__init__(piece_type, owner)
        self.value = value

    def get_value(self):
        return self.value

    def __str__(self) -> str:
        return self.piece_type + str(self.value)

    def __hash__(self) -> int:
        return hash((hash(self.piece_type), hash(self.owner_id), hash(self.value)))


class BoardAvalam(Board):
    """
    Attributes:
        env: environnement dictionnary (composed of pieces)
        dimensions: dimensions of the board
    """

    def __init__(self, env: dict[Tuple[int], PieceAvalam], dim: list[int]) -> None:
        super().__init__(env, dim)

    def __str__(self) -> str:
        dim = self.get_dimensions()
        to_print = ""
        for i in range(dim[0]):
            for j in range(dim[1]):
                if self.get_env().get((i, j), -1) != -1:
                    to_print += (
                        str(self.get_env().get((i, j)).get_type()) + str(self.get_env().get((i, j)).get_value()) + " "
                    )
                else:
                    to_print += "__ "
            to_print += "\n"
        return to_print

    def to_json(self) -> dict:
        board = [[None for _ in range(self.dimensions[1])] for _ in range(self.dimensions[0])]
        for key, value in self.env.items():
            board[key[0]][key[1]] = (value.owner_id, value.piece_type, value.value) if value is not None else None
        return {"board": board}
