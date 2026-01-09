from __future__ import annotations

from abc import abstractmethod

from seahorse.game.action import Action
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable


class Player(Serializable):
    """
    A base class representing a player in the game.

    Attributes:
        player_id (int): The ID of the player.
        name (str) : the name of the player
    """

    def __init__(self, name: str = "bob",*,player_id:int | None = None,**_) -> None:
        """
        Initializes a new instance of the Player class.

        Args:
            name (str, optional): The name of the player. Defaults to "bob".
            player_id (int, optional, keyword-only): Set the player's id in case of distant loading
        """
        self.name = name
        if player_id is None:
            self.id = id(self)
        else:
            self.id = player_id

    @abstractmethod
    def compute_action(self, **kwargs) -> Action:
        """
        Should be dedicated to adversarial search.

        Args:
            **kwargs: Additional arguments.

        Raises:
            MethodNotImplementedError: If the method is not implemented in the derived class.

        Returns:
            Action: The action to play.
        """
        raise MethodNotImplementedError()

    def get_id(self) -> int:
        """
        Returns:
            int: The ID of the player.
        """
        return self.id

    def get_name(self) -> str:
        """
        Returns:
            str: The name of the player.
        """
        return self.name

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, value: Player) -> bool:
        return hash(self) == hash(value)

    def __str__(self) -> str:
        """
        Returns a string representation of the Player object.

        Returns:
            str: The string representation.
        """
        return f"Player {self.get_name()}({self.get_id()})"


class MimicPlayer(Player):

    def __init__(self, player_type: type[Player], *args, **kwargs) -> None:
        self.mimic = player_type().__init__(*args, **kwargs)

    def compute_action(self, **kwargs) -> None:
        pass

    def __getattr__(self, attr):
        return getattr(self.mimic, attr)

    @classmethod
    def mimic_player(cls, player: Player) -> MimicPlayer:
        mimic = MimicPlayer(Player, name=player.get_name(), player_id=player.get_id())
        mimic.mimic.__dict__ |= player.__dict__

        return mimic
