from __future__ import annotations

import builtins
from abc import abstractmethod
from typing import TYPE_CHECKING

from seahorse.game.action import Action
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class Player(Serializable):
    """
    Base class representing a player in the game.

    This abstract class defines the minimal interface
    that must be implemented by any player agent.
    It is serializable and can be extended to implement players
    with specific features for many games.

    Attributes:
        id (int): Unique identifier for the player.
        name (str): Display name of the player.

    Example:
        Create and print a [Player][] object.

        ``` python
        >>> class MyPlayer(Player):
        ...     def compute_action(self, current_state, **kwargs):
        ...         # Implement adversarial search logic here
        ...         pass
        >>> player = MyPlayer(name="Alice")
        >>> print(player)
        Player Alice(140735688043456)
        ```
    """

    def __init__(self, name: str = "bob", *,
                 id: int | None = None, **_) -> None:
        """
        Initializes a new instance of the Player class.

        Args:
            name (str): Name of the player. Defaults to "bob".
            id (int | None): Identifier to assign to the player (keyword-only).
                Useful for restoring distant game states.
                If None, a unique ID is automatically generated.
            **_ (dict[str, _]):
                Additional arguments (ignored for compatibility).

        Note:
            The ID is generated using Python's built-in `id()`
            function if not provided, ensuring uniqueness
            during the execution lifetime.
        """
        self.name = name
        if id is None:
            self.id = builtins.id(self)
        else:
            self.id = id

    @abstractmethod
    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Computes the next action to play in the current game state.

        Abstract method to be implemented by subclasses.
        Should contain the adversarial search logic.

        Args:
            current_state (GameState):
                Current game state from which to compute the action.
            **kwargs (dict[str, _]):
                Additional arguments to customize the computation.
                May include:
                - `remaining_time`: Time limit for computation in seconds.
                - `depth`: Maximum search depth.
                - `heuristic`: Custom evaluation function.

        Returns:
            Action: The selected action to play.

        Raises:
            MethodNotImplementedError:
                If the method is not implemented in the derived class.
        """
        raise MethodNotImplementedError()

    def get_id(self) -> int:
        """
        Retrieves the unique identifier of the player.

        Returns:
            int: Unique numeric identifier of the player.

        Example:
            Identifiers are non-negative and unique.

            ``` python
            >>> player_1 = Player(name="Alice")
            >>> player_1.get_id() > 0
            True
            >>> player_2 = Player(name="Bob")
            >>> player_1.get_id() != player_2.get_id()
            True
            ```
        """
        return self.id

    def get_name(self) -> str:
        """
        Retrieves the name of the player.

        Returns:
            str: Display name of the player.
        """
        return self.name

    def __hash__(self) -> int:
        """
        Computes the hash of the player based on its identifier.

        Returns:
            int: Hash of the Player object.
        """
        return self.id

    def __eq__(self, value: Player) -> bool:
        """
        Compares two players for equality.

        Args:
            value (Player): Other player to compare with.

        Returns:
            bool: True if both players have the same hash (same ID),
                False otherwise.

        Note:
            Uses hashes rather than memory identity to allow comparison
            of serialized/deserialized players.
        """
        return hash(self) == hash(value)

    def __str__(self) -> str:
        """
        Human-readable representation of the player.

        Returns:
            str: Format "Player {name}({id})".

        Example:
            Rendered string format for an instance of [Player][].

            ``` python
            >>> player = Player(name="Charlie", id=123)
            >>> str(player)
            'Player Charlie(123)'
            ```
        """
        return f"Player {self.get_name()}({self.get_id()})"
