from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from coliseum.game.action import Action
from coliseum.game.time_manager import TimeMixin
from coliseum.utils.custom_exceptions import MethodNotImplementedError

if TYPE_CHECKING:
    from coliseum.game.game_state import GameState


class Player(TimeMixin):
    """
    Attributes:
        obs (Representation): representation of the game
        id_player (int): id of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    next_id = 0

    def __init__(self, name: str = "bob", time_limit=1e6) -> None:
        self.id_player = Player.next_id
        self.name = name
        Player.next_id += 1
        self.init_timer(time_limit)

    def play(self, current_state: GameState) -> Action:
        """
        Implements the player's logic, calls solve with minimal informations
        Given the problem statement one might override this to add some information
        in the solve call.

        Args:
            current_state (GameState): the current game state

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Action: The action resulting
        """
        # TODO : check score ????
        return self.solve(current_state=current_state)

    @abstractmethod
    def solve(self, **kwargs) -> Action:
        """
        Should be dedicated to adversarial search

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Action: the action to play
        """
        raise MethodNotImplementedError()

    def get_id(self):
        """
        Returns:
            int: id_player
        """
        return self.id_player

    def get_name(self):
        """
        Returns:
            str: name
        """
        return self.name

    def __str__(self) -> str:
        return f"Player {self.get_name()} has ID {self.get_id()}."
