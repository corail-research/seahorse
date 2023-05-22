from __future__ import annotations
from coliseum.game.representation import Representation
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coliseum.player.player import Player


class Piece:
    """
    Attributes:
        type: string to specify a certain type of piece
        owner: player who possess the piece
    Class attributes:
        type: -
        owner_id: id of the player
    """

    def __init__(self, type: str, owner: Player) -> None:
        self.type = type
        self.owner_id = owner.get_id()

    def get_type(self) -> str:
        """
        Returns:
            str: type string
        """
        return self.type

    def get_owner_id(self) -> int:
        """
        Returns:
            int: owner's id
        """
        return self.owner_id


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
