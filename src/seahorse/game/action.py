from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class Action:
    """
    A class representing an action in the game.

    Attributes:
        past_gs (GameState): The past game state.
        new_gs (GameState): The new game state.
    """

    def __init__(self, past_gs: GameState, new_gs: GameState) -> None:
        """
        Initializes a new instance of the Action class.

        Args:
            past_gs (GameState): The past game state.
            new_gs (GameState): The new game state.
        """
        self.past_gs = past_gs
        self.new_gs = new_gs

    def get_current_game_state(self) -> GameState:
        """
        Returns the past game state.

        Returns:
            GameState: The past game state.
        """
        return self.past_gs

    def get_next_game_state(self) -> GameState:
        """
        Returns the new game state.

        Returns:
            GameState: The new game state.
        """
        return self.new_gs

    def __hash__(self) -> int:
        return hash((hash(self.get_next_game_state()), hash(self.get_current_game_state())))

    def __eq__(self, value: object) -> bool:
        return hash(self) == hash(value)

    def __str__(self) -> str:
        return "From:\n" + self.get_current_game_state().get_rep().__str__() + "\nto:\n" + self.get_next_game_state().get_rep().__str__()
