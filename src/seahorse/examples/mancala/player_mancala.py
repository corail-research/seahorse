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

    def to_json(self) -> str:
        return {i:j for i,j in self.__dict__.items() if i!="timer"}

    @classmethod
    def from_json(cls, data) -> Serializable:
        return PlayerMancala(**json.loads(data))
