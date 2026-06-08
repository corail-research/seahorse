from abc import abstractmethod
from typing import Any

from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable


class Representation(Serializable):
    """
    Abstract base class for representing the state of a game.

    The Representation class encapsulates the game state in a structured format
    that serves two main purposes:

    1. **Game Logic**:
        Contains game state data (board positions, piece coordinates, etc.)
        that GameState uses to compute possible actions and validate moves.
    2. **Display/Visualization**:
        Provides a format suitable for display by a GUI,
        comparison between states, and serialization.

    For Game Designers:
        *MUST* extend this class or the
        [Board][...game_layout.board.Board] subclass
        and implement abstract methods
        to define game-specific state representation.

    Attributes:
        env (dict): Dictionary containing the game state representation.
    """

    def __init__(self, env: dict) -> None:
        """
        Initializes a new Representation instance with the given environment.

        Args:
            env (dict): Dictionary containing both game logic and display data.

        Note:
            The `env` dictionary structure should be designed to efficiently
            support both game computations and display. Game logic data takes
            priority, as it's essential for the game to function. Data should
            also be easily serializable and hashable.
        """
        self.env = env

    def get_env(self) -> dict:
        """
        Retrieves the complete environment dictionary.

        Returns:
            dict: The environment dictionary.
        """
        return self.env

    # TODO: This should probably be reworked.
    # In some case, we cannot distinguish if the key was found or not.
    def find(self, to_find: Any) -> Any:
        """
        Searches for a key directly in the environment dictionary.

        This is a convenience method for accessing specific game state
        values needed for game logic computations.

        Args:
            to_find (Any): The key to search for in the environment dictionary.

        Returns:
            Any: The value associated with the key if found, otherwise -1.
        """
        if to_find not in self.env.keys():
            return -1
        else:
            return self.env[to_find]

    @abstractmethod
    def __hash__(self) -> int:
        """
        Computes a hash value for the representation based on game state.

        **Abstract method - MUST be implemented by game designers**

        Returns:
            int: Hash value of the game state representation.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - **Critical for game performance**: Used extensively for state
              caching, transposition tables, and duplicate detection
            - Avoid hashing display-only data
        """
        raise MethodNotImplementedError()

    # TODO: Maybe this function can already be implemented with hash.
    @abstractmethod
    def __eq__(self, __value: object) -> bool:
        """
        Compares two representations for game state equality.

        **Abstract method - MUST be implemented by game designers**

        Args:
            __value (object): Other object to compare with.

        Returns:
            bool: True if both representations represent the same game state,
                False otherwise.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - **Used by [GameState][....game_state.GameState]
              for state comparison**: Essential for
              detecting repeated positions and caching
            - Should compare essential game state data for efficiency
            - Must be consistent with __hash__ (equal states have equal hashes)
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        """
        Creates a human-readable string representation of the game state.

        **Abstract method - MUST be implemented by game designers**

        Returns:
            str: String representation suitable for display, debugging,
                and logging.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.
        """
        raise MethodNotImplementedError()
