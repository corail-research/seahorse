import copy

from coliseum.game.game_layout.board import Piece
from coliseum.game.representation import Representation


class BoardMancala(Representation):
    """
    Attributes:
        env: environnement dictionnary (composed of pieces)
        dimensions: dimensions of the board
    """

    def __init__(self,env = None) -> None:
        if env is None:
            single_piece = Piece("rock", None)
            env = {(0,0):[],(1,6):[]}
            for i in range(1,7):
                env[(0,i)] = [single_piece.copy() for _ in range(4)]
                env[(1,i-1)] = [single_piece.copy() for _ in range(4)]
        super().__init__(env)

    def __str__(self) -> str:
        to_print = " "*8
        for i in range(1,7):
            to_print += "  " + str(len(self.env[(0,i)])) + "   "
        to_print += "\n"
        length = len(to_print)-8
        to_print+= "  ("+str(len(self.env[(0,0)]))+")  "+"-"*length+"  ("+str(len(self.env[(1,6)]))+")  \n"
        to_print+=" "*8
        for i in range(6):
            to_print += "  " + str(len(self.env[(1,i)])) + "   "
        to_print += "\n"
        return to_print

    def __hash__(self) -> int:
        return hash(frozenset([(hash(pos),hash(piece)) for pos,piece in self.env.items()]))

    def copy(self):
        return BoardMancala(copy.deepcopy(self.env))

