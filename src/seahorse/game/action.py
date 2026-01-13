from __future__ import annotations

from abc import abstractmethod

from seahorse.utils.serializer import Serializable


class Action(Serializable):
    """
    A generic class representing an action in the game.

    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the Action class.

        """
        pass

    @abstractmethod
    def get_stateful_action(self, *args, **kwargs) -> Action:
        """
        Returns the stateful action.

        Returns:
            Action: The stateful action.
        """
        raise NotImplementedError

