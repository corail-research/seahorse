import json

from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class PlayerAbalone(Player):
    """
    A player class implementing the Alpha-Beta algorithm for the Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", **kwargs) -> None:
        """
        Initializes a new instance of the AlphaPlayerAbalone class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str, optional): The name of the player. Defaults to "bob".
        """
        super().__init__(name,**kwargs)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        """
        Gets the type of the player's game piece.

        Returns:
            str: The type of the player's game piece.
        """
        return self.piece_type

    def toJson(self) -> str:
        return json.dumps(self.__dict__,default=lambda x:x.toJson() if isinstance(x,Serializable) else None)

    @classmethod
    def fromJson(cls, data) -> Serializable:
        return PlayerAbalone(**json.loads(data))
