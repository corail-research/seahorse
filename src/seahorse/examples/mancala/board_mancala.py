import copy

from seahorse.game.game_layout.board import Piece
from seahorse.game.representation import Representation


class PieceMancala(Piece):
    """
    A class representing a piece in the game of Mancala.

    Attributes:
        value (int): The value associated with the piece.

    Args:
        value (int): The value of the piece.
    """

    def __init__(self, value: int) -> None:
        """
        Initializes a new instance of the PieceMancala class.

        Args:
            value (int): The value of the piece.
        """
        super().__init__(None, None)
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


class BoardMancala(Representation):
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
        super().__init__(env)

    def copy(self):
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
