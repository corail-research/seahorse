from __future__ import annotations

from typing import TYPE_CHECKING

from seahorse.game.action import Action
from seahorse.game.stateful_action import StatefulAction
from seahorse.utils.custom_exceptions import NoGameStateProvidedError

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class StatelessAction(Action):
    """
    A class representing an action in the game.

    Attributes:
        data (dict): The data of the stateless action.
    """

    def __init__(self, data: dict) -> None:
        """
        Initializes a new instance of the Action class.

        Args: data (dict): The data of the stateless action.

        """
        self.data = data


    def get_stateful_action(self, game_state: GameState) -> StatefulAction:
        """
        Returns the stateful action.

        Returns:
            StatefulAction: The stateful action.
        """
        if game_state is None:
            raise NoGameStateProvidedError()

        return StatefulAction(game_state, game_state.apply_action(self))


    def __hash__(self) -> int:
        return hash(tuple(self.data.items()))

    def __eq__(self, value: object) -> bool:
        return hash(self) == hash(value)

    def __str__(self) -> str:
        return "StatelessAction: " + str(self.data)

    def to_json(self) -> dict:
        return self.__dict__
