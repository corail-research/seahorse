from __future__ import annotations

import builtins
from abc import abstractmethod
from typing import TYPE_CHECKING

from seahorse.game.action import Action
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState

class Player(Serializable):
    """
    A base class representing a player in the game.

    Attributes:
        id (int): The ID of the player.
        name (str) : the name of the player
    """

    def __init__(self, name: str = "bob",*,id:int | None = None,**_) -> None:
        """
        Initializes a new instance of the Player class.

        Args:
            name (str, optional): The name of the player. Defaults to "bob".
            id (int, optional, keyword-only): Set the player's id in case of distant loading
        """
        self.name = name
        if id is None:
            self.id = builtins.id(self)
        else:
            self.id = id

    @abstractmethod
    def compute_action(self, current_state: GameState, **kwargs) -> Action:
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

    # @abstractmethod
    # def to_mimic(self) -> MimicPlayer:
    #     raise MethodNotImplementedError()

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

class MimicPlayer(Serializable):

    def __init__(self, player_type: type[Player], *args, **kwargs) -> None:
        self.mimic = player_type(*args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self.mimic, attr)

    def __str__(self) -> str:
        return f"MimicPlayer {self.get_name()}({self.get_id()})"

    def to_json(self) -> dict:
        return self.mimic.__dict__
