from __future__ import annotations

import ast

from seahorse.player.player import Player


class PlayerTictac(Player):
    """
    A player class for Tic Tac Toe.

    Attributes:
        piece_type (str): the type of the player.
    """

    def __init__(self, piece_type: str, name: str = "bob", **kwargs) -> None:
        """
        Initializes a new instance of the PlayerTictac class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str): The name of the player.
        """
        super().__init__(name,**kwargs)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        """
        Returns:
            str: The type of the player's game piece.
        """
        return self.piece_type


    def to_json(self) -> dict:
        return {i:j for i,j in self.__dict__.items() if not i.startswith("_")}

    @classmethod
    def from_json(cls, data) -> "PlayerTictac":
        if isinstance(data, str):
            data = ast.literal_eval(data)
        return PlayerTictac(**data)