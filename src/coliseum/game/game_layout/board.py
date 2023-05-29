from __future__ import annotations

from typing import TYPE_CHECKING

from coliseum.game.representation import Representation

if TYPE_CHECKING:
    from coliseum.player.player import Player


class Piece:
    """
    Attributes:
        piece_type: string to specify a certain type of piece
        owner: player who possess the piece
    """

    def __init__(self, piece_type: str, owner: Player) -> None:
        self.piece_type = piece_type
        self.owner_id = owner.get_id()

    def get_type(self) -> str:
        """
        Returns:
            str: type string
        """
        return self.piece_type

    def get_owner_id(self) -> int:
        """
        Returns:
            int: owner's id
        """
        return self.owner_id

    def __str__(self) -> str:
        return self.get_type()

    def __hash__(self) -> int:
        return hash((hash(self.get_type()),hash(self.owner_id)))


class Board(Representation):
    """
    Attributes:
        env: environnement dictionnary (composed of pieces)
        dimensions: dimensions of the board
    """

    def __init__(self, env: dict[tuple[int], Piece], dim: list[int]) -> None:
        super().__init__(env)
        self.dimensions = dim

    def get_dimensions(self) -> list[int]:
        """
        Returns:
            list[int]: list of dimensions
        """
        return self.dimensions

    def get_pieces_player(self, owner: Player) -> tuple[int, list[Piece]]:
        """
        Function to know the pieces of the player specified

        Args:
            owner (Player): player specified

        Returns:
            tuple[int, list[Piece]]: number of pieces of the player, list of the pieces of the player
        """
        pieces_list = []
        number = 0
        for key in self.env.keys():
            if self.env[key].get_owner_id() == owner.get_id():
                number += 1
                pieces_list.append(key)
        return number, pieces_list

    def __str__(self) -> str:
        dim = self.get_dimensions()
        to_print = ""
        for i in range(dim[0]):
            for j in range(dim[1]):
                if self.get_env().get((i, j), -1) != -1:
                    to_print += str(self.get_env().get((i, j)).get_type()) + " "
                else:
                    to_print += "_ "
            to_print += "\n"
        return to_print

    def __hash__(self):
        return hash(frozenset([(hash(pos),hash(piece)) for pos,piece in self.env.items()]))
