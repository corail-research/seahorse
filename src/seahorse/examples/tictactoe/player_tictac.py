import json
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


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
    
        
    def toJson(self) -> str:
        return json.dumps(self.__dict__,default=lambda x:x.toJson() if isinstance(x,Serializable) else None)
    
    @classmethod
    def fromJson(cls, data) -> Serializable:
        return PlayerTictac(**json.loads(data))

