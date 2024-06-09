from __future__ import annotations

from typing import TYPE_CHECKING

from seahorse.game.action import Action

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class HeavyAction(Action):
    """
    A class representing an action in the game.

    Attributes:
        past_gs (GameState): The past game state.
        new_gs (GameState): The new game state.
    """

    def __init__(self, current_game_state: GameState, next_game_state: GameState) -> None:
        """
        Initializes a new instance of the Action class.

        Args:
            past_gs (GameState): The past game state.
            new_gs (GameState): The new game state.
        """
        self.current_game_state = current_game_state
        self.next_game_state = next_game_state

    def get_current_game_state(self) -> GameState:
        """
        Returns the past game state.

        Returns:
            GameState: The past game state.
        """
        return self.current_game_state

    def get_next_game_state(self) -> GameState:
        """
        Returns the new game state.

        Returns:
            GameState: The new game state.
        """
        return self.next_game_state

    def get_heavy_action(self, *_) -> HeavyAction:
        """
        Returns the heavy action.

        Returns:
            HeavyAction: The heavy action.
        """
        return self

    def __hash__(self) -> int:
        return hash((hash(self.get_next_game_state()), hash(self.get_current_game_state())))

    def __eq__(self, value: object) -> bool:
        return hash(self) == hash(value)

    def __str__(self) -> str:
        return "From:\n" + self.get_current_game_state().get_rep().__str__() + "\nto:\n" + self.get_next_game_state().get_rep().__str__()

    def to_json(self) -> dict:
        return self.__dict__
