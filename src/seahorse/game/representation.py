from abc import abstractmethod
from typing import Any

from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable


class Representation(Serializable):
    """
    A class representing a game representation.

    Attributes:
        env (dict): The dictionary of the current state.
    """

    def __init__(self, env: dict) -> None:
        """
        Initializes a new instance of the Representation class.

        Args:
            env (dict): The dictionary of the current state.
        """
        self.env = env

    def get_env(self) -> dict:
        """
        Gets the dictionary of the environment.

        Returns:
            dict: The dictionary of the environment.
        """
        return self.env

    def find(self, to_find: Any) -> Any:
        """
        Finds a key directly in the environment.

        Args:
            to_find (Any): The key to find.

        Returns:
            Any: The value of the cell.
        """
        if to_find not in self.env.keys():
            return -1
        else:
            return self.env[to_find]

    @abstractmethod
    def __hash__(self) -> int:
        raise MethodNotImplementedError()

    @abstractmethod
    def __eq__(self, __value: object) -> bool:
        raise MethodNotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        raise MethodNotImplementedError()
