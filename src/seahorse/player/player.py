from __future__ import annotations

from abc import abstractmethod
import builtins
import json
from typing import TYPE_CHECKING, Any, Coroutine

from seahorse.game.action import Action
from seahorse.game.io_stream import EventMaster, EventSlave, event_emitting, remote_action
from seahorse.game.time_manager import TimeMixin
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class Player(TimeMixin,Serializable):
    """
    A base class representing a player in the game.

    Attributes:
        id (int): The ID of the player.
        name (str) : the name of the player
    """

    def __init__(self, name: str = "bob", time_limit: float = 1e6,*,id:int=None,**kwargs) -> None:
        """
        Initializes a new instance of the Player class.

        Args:
            name (str, optional): The name of the player. Defaults to "bob".
            time_limit (float, optional): The time limit for the player's moves. Defaults to 1e6.
            hard_id (int, optional, keyword-only): Set the player's id in case of distant loading
        """
        self.name = name
        self.init_timer(time_limit)
        if id==None:
            self.id = builtins.id(self)
        else:
            self.id = id

    def play(self, current_state: GameState) -> Action:
        """
        Implements the player's logic and calls solve with minimal information.

        Args:
            current_state (GameState): The current game state.

        Raises:
            MethodNotImplementedError: If the method is not implemented in the derived class.

        Returns:
            Action: The resulting action.
        """
        # TODO: check score ????
        return self.solve(current_state=current_state)

    @abstractmethod
    def solve(self, **kwargs) -> Action:
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

    def get_id(self):
        """
        Returns:
            int: The ID of the player.
        """
        return self.id

    def get_name(self):
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
        return f"Player {self.get_name()} has ID {self.get_id()}."
