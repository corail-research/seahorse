import json

from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class PlayerMancala(Player):
    """
    A class representing a Mancala player.

    Attributes:
        name (str): The name of the player.

    Args:
        name (str): The name of the player.
    """

    def __init__(self, name: str = "bob", **kwargs) -> None:
        """
        Initializes a new instance of the PlayerMancala class.

        Args:
            name (str): The name of the player.
        """
        super().__init__(name, **kwargs)

    def toJson(self) -> str:
        return json.dumps(self.__dict__,default=lambda x:x.toJson() if isinstance(x,Serializable) else None)

    @classmethod
    def fromJson(cls, data) -> Serializable:
        return PlayerMancala(**json.loads(data))
