from __future__ import annotations

from typing import TYPE_CHECKING

from seahorse.game.action import Action
from seahorse.game.stateful_action import StatefulAction
from seahorse.utils.custom_exceptions import NoGameStateProvidedError

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class StatelessAction(Action):
    """
    Lightweight, serializable action representation
    without embedded game state.

    This class only contains transition data that can be applyed
    to [game state][...game_state.GameState] to compute another
    game state resulting from the action.

    Few benefits from a stateless implementation:
        - Enable reduced memory footprint compared to
        [StatefulAction][...stateful_action.StatefulAction]
        - Separation of action data from game state logic
        - Can be cached and reused across different game states

    Attributes:
        data (dict): Dictionary containing all action parameters in a
            JSON-serializable format.
    """

    def __init__(self, data: dict) -> None:
        """
        Initializes a StatelessAction with serializable data.

        Args:
            data (dict):
                JSON-serializable dictionary containing all action parameters.
                Must include everything needed to reconstruct the action
                in a game state context.

        Note:
            The data should be kept minimal to optimize serialization
            and transmission. Avoid storing computed or derived values.

        """
        self.data = data

    def get_stateful_action(self, game_state: GameState) -> StatefulAction:
        """
        Converts this stateless action to a
        [StatefulAction][....stateful_action.StatefulAction] by applying it
        to a specific game state.

        Args:
            game_state (GameState):
                The current game state to apply the action to.
                Must not be None.

        Returns:
            StatefulAction: A fully-contextualized action containing both
                source and resulting game states.

        Raises:
            NoGameStateProvidedError: If game_state is None.

        Note:
            This method delegates to
            [apply_action][....game_state.GameState.apply_action] to
            compute the resulting state.
            The [GameState][....game_state.GameState]
            subclass must implement this method
            to handle this specific action type.
        """
        if game_state is None:
            raise NoGameStateProvidedError()

        return StatefulAction(game_state, game_state.apply_action(self))

    def __hash__(self) -> int:
        """
        Computes a hash based on the action's data.

        Returns:
            int: Hash value for use in dictionaries and sets.
        """
        return hash(tuple(self.data.items()))

    def __eq__(self, value: StatelessAction) -> bool:
        """
        Compares two StatelessActions for equality.

        Args:
            value (StatelessAction):
                Other StatelessAction to compare with.

        Returns:
            bool: True if both actions have the same data, False otherwise.
        """
        return hash(self) == hash(value)

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: String representation showing the action data.
        """
        return "StatelessAction: " + str(self.data)

    def to_json(self) -> dict:
        """
        Serializes the action to a JSON-compatible dictionary.

        Returns:
            dict: Dictionary containing all action data, ready for
                network transmission or storage.
        """
        return self.__dict__
