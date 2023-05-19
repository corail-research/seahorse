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

    def __init__(self, name: str = "bob") -> None:
        self.id_player = Player.next_id
        self.name = name
        Player.next_id += 1

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

        return Action(current_state.get_rep(),
                      self.solve(
                          current_rep=current_state.get_rep(),
                          scores=current_state.get_scores()
        ))

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

    @abstractmethod
    def check_action(self, action: Action) -> bool:
        """

        Must return `True` if the current action is allowed.

        Args:
            player (Player): the originating player

        Raises:
            MethodNotImplementedError: _description_
        """
        raise MethodNotImplementedError()

    def get_id(self):
        """
        Returns:
            int: id_player
        """
        return self.id_player
