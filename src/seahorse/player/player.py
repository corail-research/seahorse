from __future__ import annotations

import builtins
from abc import abstractmethod
from typing import TYPE_CHECKING

from seahorse.game.action import Action
# from seahorse.game.time_manager import TimeMixin, timed_function
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
            hard_id (int, optional, keyword-only): Set the player's id in case of distant loading
        """
        self.name = name
        if id is None:
            self.id = builtins.id(self)
        else:
            self.id = id


    def play(self, current_state: GameState, remaining_time: int) -> Action:
        """
        Implements the player's logic and calls compute_action with minimal information.

        Args:
            current_state (GameState): The current game state.

        Raises:
            MethodNotImplementedError: If the method is not implemented in the derived class.

        Returns:
            Action: The resulting action.
        """
        # TODO: check score ????
        return self.compute_action(current_state=current_state, remaining_time=remaining_time)

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

    def __str__(self) -> str:
        """
        Returns a string representation of the Player object.

        Returns:
            str: The string representation.
        """
        return f"Player {self.get_name()}({self.get_id()})"
