import json
from typing import Tuple

from seahorse.game.game_layout.board import Board, Piece
from seahorse.utils.serializer import Serializable


class BoardTictac(Board):
    """
    A class representing a Tic-Tac-Toe game board.

    Attributes:
        env (dict[Tuple[int], Piece]): The environment dictionary composed of pieces.
        dimensions (list[int]): The dimensions of the board.
    """

    def __init__(self, env: dict[Tuple[int], Piece], dim: list[int]) -> None:
        """
        Initializes a new instance of the BoardTictac class.

        Args:
            env (dict[Tuple[int], Piece]): The environment dictionary composed of pieces.
            dim (list[int]): The dimensions of the board.
        """
        super().__init__(env, dim)

    def __str__(self) -> str:
        return super().__str__()

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
        for x,y in d['env'].items():
            # TODO eval is unsafe
            del dd['env'][x]
            dd['env'][eval(x)] = Piece(**json.loads(y))
        return cls(**dd)
