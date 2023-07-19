from __future__ import annotations

import copy
import json

from seahorse.game.game_layout.board import Board, Piece
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class PieceMancala(Piece):
    """
    A class representing a piece in the game of Mancala.

    Attributes:
        value (int): The value associated with the piece.

    Args:
        value (int): The value of the piece.
    """

    def __init__(self, value: int, piece_type: str= None, owner: Player=None, owner_id: int=-1) -> None:
        """
        Initializes a new instance of the PieceMancala class.

        Args:
            value (int): The value of the piece.
        """
        super().__init__(piece_type,owner,owner_id)
        self.value = value

    def remove(self) -> int:
        """
        Removes the piece from the game and returns its value.

        Returns:
            int: The value of the piece.
        """
        val = self.value
        self.value = 0
        return val

    def increment(self, val: int = 1) -> None:
        """
        Increments the value of the piece.

        Args:
            val (int): The value to increment by.
        """
        self.value += val

    def get_value(self) -> int:
        """
        Returns the value of the piece.

        Returns:
            int: The value of the piece.
        """
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def toJson(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def fromJson(cls,data) -> str:
        return cls(**json.loads(data))


class BoardMancala(Board):
    """
    Represents the Mancala board.

    Attributes:
        env (dict): Environment dictionary composed of pieces.
        dimensions (tuple): Dimensions of the board.
    """

    def __init__(self, env=None) -> None:
        """
        Initializes the BoardMancala object.

        Args:
            env (dict, optional): Environment dictionary representing the board. Defaults to None.
        """
        if env is None:
            env = {(0,0):PieceMancala(0),(1,6):PieceMancala(0)}
            for i in range(1,7):
                env[(0,i)] = PieceMancala(4)
                env[(1,i-1)] = PieceMancala(4)
        super().__init__(env,[2,7])

    def copy(self) -> BoardMancala :
        """
        Creates a copy of the board.

        Returns:
            BoardMancala: Copied BoardMancala object.
        """
        return BoardMancala(copy.deepcopy(self.env))

    def __hash__(self) -> int:
        return hash(frozenset([(hash(pos), hash(piece)) for pos, piece in self.env.items()]))

    def __str__(self) -> str:
        to_print = " "*8
        for i in range(1,7):
            to_print += "  " + str(self.env[(0,i)]) + "   "
        to_print += "\n"
        length = len(to_print)-8
        to_print+= "  ("+str(self.env[(0,0)])+")  "+"-"*length+"  ("+str(self.env[(1,6)])+")  \n"
        to_print+=" "*8
        for i in range(6):
            to_print += "  " + str(self.env[(1,i)]) + "   "
        to_print += "\n"
        return to_print

    def toJson(self) -> dict:
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
    def fromJson(cls, data) -> Serializable:
        d = json.loads(data)
        dd = json.loads(data)
        for x,y in d["env"].items():
            # TODO eval is unsafe
            del dd["env"][x]
            dd["env"][eval(x)] = PieceMancala(**json.loads(y))
        return cls(**dd)
