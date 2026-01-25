import json

from seahorse.game.game_layout.board import Board, Piece
from seahorse.utils.serializer import Serializable


class BoardTictac(Board):
    """
    A class representing a game board.

    Attributes:
        env (dict[Tuple[int], Piece]): The environment dictionary composed of pieces.
        dimensions (list[int]): The dimensions of the board.
    """

    def __init__(self, env: dict[tuple[int], Piece], dim: list[int]) -> None:
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
        return {"env":{str(x):y for x,y in self.env.items()},"dim":self.dimensions}

    @classmethod
    def from_json(cls, data) -> Serializable:
        d = json.loads(data)
        dd = json.loads(data)
        for x,y in d["env"].items():
            # TODO eval is unsafe
            del dd["env"][x]
            dd["env"][eval(x)] = Piece.from_json(json.dumps(y))
        return cls(**dd)