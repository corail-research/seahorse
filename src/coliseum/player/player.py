from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from coliseum.game.action import Action
from coliseum.game.representation import Representation
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
        self.possible_actions: list[Representation] = []
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

        return Action(
            current_state.get_rep(), self.solve(possible_actions=current_state.get_possible_actions(),
                                                scores=current_state.get_scores())
        )

    @abstractmethod
    def solve(self, **kwargs) -> Representation:
        """
        Should be dedicated to adversarial search

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Representation: the next state representation
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
