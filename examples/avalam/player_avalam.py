import json

from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class PlayerAvalam(Player):
    """
    Player class for Avalam game that uses the alpha-beta algorithm for move selection.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob",  **kwargs) -> None:
        """
        Initialize the AlphaPlayerAvalam instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
        """
        super().__init__(name, **kwargs)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        """
        Get the type of the player's game piece.

        Returns:
            str: Piece type string representing the type of the piece
        """
        return self.piece_type

    def to_json(self) -> str:
        return json.dumps(self.__dict__,default=lambda x:x.to_json() if isinstance(x,Serializable) else None)

    @classmethod
    def from_json(cls, data) -> Serializable:
        return PlayerAvalam(**json.loads(data))
