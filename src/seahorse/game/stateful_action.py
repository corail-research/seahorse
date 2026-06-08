from __future__ import annotations

from typing import TYPE_CHECKING

from seahorse.game.action import Action

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class StatefulAction(Action):
    """
    Complete action representation with embedded
    [game state][...game_state.GameState] context.

    This class contains both source and destination game states and
    is the most straight forward representation of state transition.
    StatefulActions are also used to validate
    [players][....player.player.Player]
    computed action with game state
    [get_possible_stateful_actions]
    [...game_state.GameState.get_possible_stateful_actions] method.

    Attributes:
        current_game_state (GameState): The game state before the action.
        next_game_state (GameState): The game state after applying the action.
    """

    def __init__(self, current_game_state: GameState,
                 next_game_state: GameState) -> None:
        """
        Initializes a StatefulAction with source and destination game states.

        Args:
            current_game_state (GameState): The game state before the action.
            next_game_state (GameState): The resulting game state after
                the action.

        Note:
            The `next_game_state` should be the result of applying this
            specific action to the `current_game_state`.
        """
        self.current_game_state = current_game_state
        self.next_game_state = next_game_state

    def get_current_game_state(self) -> GameState:
        """
        Retrieves the source game state.

        Returns:
            GameState: The game state before the action was applied.
        """
        return self.current_game_state

    def get_next_game_state(self) -> GameState:
        """
        Retrieves the resulting game state.

        Returns:
            GameState: The game state after applying the action.
        """
        return self.next_game_state

    def get_stateful_action(self, *_) -> StatefulAction:
        """
        Returns self since this action is already stateful.

        Args:
            *_ (tuple[_,...]):
                Ignored arguments (for compatibility with abstract method).

        Returns:
            StatefulAction: This same instance.

        Note:
            Since `StatefulAction` already contains game state information,
            this method simply returns `self` without creating a new object.
        """
        return self

    def __hash__(self) -> int:
        """
        Computes a hash based on both game states.

        Returns:
            int: Combined hash of current and next game states.
        """
        return hash((hash(self.get_next_game_state()),
                     hash(self.get_current_game_state())))

    def __eq__(self, value: object) -> bool:
        """
        Compares two StatefulActions for equality.

        Args:
            value (object): Other object to compare with.

        Returns:
            bool:
                True if both actions have
                the same current and
                next game states.
        """
        return hash(self) == hash(value)

    def __str__(self) -> str:
        """
        Detailed string representation showing state transition.

        Returns:
            str: Multiline string showing
                the transition between
                game states.
        """
        return "From:\n" + self.get_current_game_state().get_rep().__str__() \
            + "\nto:\n" + self.get_next_game_state().get_rep().__str__()

    def to_json(self) -> dict:
        """
        Serializes the action to a JSON-compatible dictionary.

        Returns:
            dict: Dictionary containing both game states.
        """
        return self.__dict__
