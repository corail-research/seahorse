from __future__ import annotations

import json
from typing import TYPE_CHECKING

from seahorse.game.representation import Representation
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.player.player import Player


class Piece(Serializable):
    """
    A class representing a piece in the game.

    Attributes:
        piece_type (str): The type of the piece.
        owner_id (int): The ID of the player who possesses the piece.
    """

    def __init__(self, piece_type: str, owner: Player | None = None, owner_id: int=-1) -> None:
        """
        Initializes a new instance of the Piece class.

        Args:
            piece_type (str): The type of the piece.
            owner (Player): The player who possesses the piece.
        """
        self.piece_type = piece_type
        if owner is None:
            self.owner_id = owner_id
        else:
            self.owner_id = owner.get_id()

    def get_type(self) -> str:
        """
        Gets the type of the piece.

        Returns:
            str: The type of the piece.
        """
        return self.piece_type

    def get_owner_id(self) -> int:
        """
        Gets the ID of the owner of the piece.

        Returns:
            int: The ID of the owner.
        """
        return self.owner_id

    def copy(self) -> Piece:
        """
        Creates a copy of the piece.

        Returns:
            Piece: A copy of the piece.
        """
        return Piece(self.piece_type, None)

    def __hash__(self) -> int:
        return hash((hash(self.get_type()), hash(self.owner_id)))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    #def __str__(self) -> str:
    #    return self.get_type()

    def to_json(self) -> str:
        return self.__dict__

    @classmethod
    def from_json(cls,data) -> str:
        return cls(**json.loads(data))


class Board(Representation):
    """
    A class representing the game board.

    Attributes:
        env (dict[Tuple[int], Piece]): The environment dictionary composed of pieces.
        dimensions (list[int]): The dimensions of the board.
    """

    def __init__(self, env: dict[tuple[int], Piece], dim: list[int]) -> None:
        """
        Initializes a new instance of the Board class.

        Args:
            env (dict[Tuple[int], Piece]): The environment dictionary composed of pieces.
            dim (list[int]): The dimensions of the board.
        """
        super().__init__(env)
        self.dimensions = dim

    def get_dimensions(self) -> list[int]:
        """
        Gets the dimensions of the board.

        Returns:
            list[int]: The list of dimensions.
        """
        return self.dimensions

    def get_pieces_player(self, owner: Player) -> tuple[int, list[Piece]]:
        """
        Gets the pieces owned by a specific player.

        Args:
            owner (Player): The player specified.

        Returns:
            Tuple[int, list[Piece]]: The number of pieces owned by the player and the list of their pieces.
        """
        pieces_list = []
        number = 0
        for key in self.env.keys():
            if self.env[key].get_owner_id() == owner.get_id():
                number += 1
                pieces_list.append(key)
        return number, pieces_list

    def __hash__(self):
        return hash(frozenset([(hash(pos), hash(piece)) for pos, piece in self.env.items()]))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

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
