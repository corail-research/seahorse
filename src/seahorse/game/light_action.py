from __future__ import annotations

from typing import TYPE_CHECKING

from seahorse.game.action import Action
from seahorse.game.heavy_action import HeavyAction
from seahorse.utils.custom_exceptions import NoGameStateProvidedError

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class LightAction(Action):
    """
    A class representing an action in the game.

    Attributes:
        data (dict): The data of the light action.
    """

    def __init__(self, data: dict) -> None:
        """
        Initializes a new instance of the Action class.

        Args: data (dict): The data of the light action.

        """
        self.data = data


    def get_heavy_action(self, game_state: GameState = None) -> HeavyAction:
        """
        Returns the heavy action.

        Returns:
            HeavyAction: The heavy action.
        """
        if game_state is None:
            raise NoGameStateProvidedError()

        return HeavyAction(game_state, game_state.apply_action(self))


    def __hash__(self) -> int:
        return hash(tuple(self.data.items()))

    def __eq__(self, value: object) -> bool:
        return hash(self) == hash(value)

    def __str__(self) -> str:
        return "LightAction: " + str(self.data)

    def to_json(self) -> dict:
        return self.__dict__
