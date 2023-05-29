from abc import abstractmethod
from typing import Any

from coliseum.utils.custom_exceptions import MethodNotImplementedError


class Representation:
    """
    Attributes:
        env: dict of the current state
    """

    def __init__(self, env: dict) -> None:
        self.env = env

    def get_env(self) -> dict:
        """
        Returns:
            dict: dictionnary of the environnement
        """
        return self.env

    def find(self, to_find: Any) -> Any:
        """
        Function to fin a key directly in the environnement

        Args:
            to_find (Any): key to find

        Returns:
            Any: return the cell
        """
        if to_find not in self.env.keys():
            return -1
        else:
            return self.env[to_find]

    @abstractmethod
    def __hash__(self) -> int:
        raise MethodNotImplementedError()
