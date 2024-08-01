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
    def get_heavy_action(self, *_) -> Action:
        """
        Returns the heavy action.

        Returns:
            Action: The heavy action.
        """
        raise NotImplementedError

