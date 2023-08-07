from __future__ import annotations

import json
from typing import TYPE_CHECKING

from seahorse.game.game_layout.board import Board, Piece
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.player.player import Player


class PieceAvalam(Piece):
    """
    Piece class for the Avalam game.

    Attributes:
        piece_type (str): Type of the piece
        owner (Player): Owner of the piece
        value (int): Value of the piece
    """

    def __init__(self, piece_type: str, owner: Player=None, owner_id: int=-1, value: int=1) -> None:
        """
        Initialize the PieceAvalam instance.

        Args:
            piece_type (str): Type of the piece
            owner (Player): Owner of the piece
            value (int): Value of the piece
        """
        super().__init__(piece_type, owner, owner_id)
        self.value = value

    def get_value(self) -> int:
        """
        Get the value of the piece.

        Returns:
            int: Value of the piece
        """
        return self.value

    def __hash__(self) -> int:
        return hash((hash(self.piece_type), hash(self.owner_id), hash(self.value)))

    def __str__(self) -> str:
        return self.piece_type + str(self.value)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls,data) -> str:
        return cls(**json.loads(data))


class BoardAvalam(Board):
    """
    Board class for the Avalam game.

    Attributes:
        env (dict[Tuple[int], PieceAvalam]): Environment dictionary composed of pieces
        dimensions (list[int]): Dimensions of the board
    """

    def __init__(self, env: dict[tuple[int], PieceAvalam], dim: list[int]) -> None:
        """
        Initialize the BoardAvalam instance.

        Args:
            env (dict[Tuple[int], PieceAvalam]): Environment dictionary composed of pieces
            dim (list[int]): Dimensions of the board
        """
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
        """
        Converts the board to a JSON object.

        Returns:
            dict: The JSON representation of the board.
        """
        # TODO: migrate below into js code
        #board = [[None for _ in range(self.dimensions[1])] for _ in range(self.dimensions[0])]
        #for key, value in self.env.items():
        #    board[key[0]][key[1]] = value.piece_type if value is not None else None
        #return {"board": board}
        return {"env":{str(x):y for x,y in self.env.items()},"dim":self.dimensions}

    @classmethod
    def from_json(cls, data) -> Serializable:
        d = json.loads(data)
        dd = json.loads(data)
        for x,y in d["env"].items():
            # TODO eval is unsafe
            del dd["env"][x]
            dd["env"][eval(x)] = PieceAvalam(**json.loads(y))
        return cls(**dd)