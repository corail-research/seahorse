from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Coroutine

from seahorse.game.action import Action
from seahorse.game.io_stream import EventMaster, EventSlave, event_emitting, remote_action
from seahorse.game.timer import Timer
from seahorse.utils.custom_exceptions import MethodNotImplementedError

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class Player():
    """
    A base class representing a player in the game.

    Attributes:
        id (int): The ID of the player.
        name (str) : the name of the player
    """

    def __init__(self, name: str = "bob", time_limit: float = 1e6) -> None:
        """
        Initializes a new instance of the Player class.

        Args:
            name (str, optional): The name of the player. Defaults to "bob".
            time_limit (float, optional): The time limit for the player's moves. Defaults to 1e6.
        """
        self.name = name
        self.id = id(self)
        self.timer = Timer(time_limit=time_limit)

    def play(self, current_state: GameState) -> Action:
        """
        Implements the player's logic and calls compute_action with minimal information.

        Args:
            current_state (GameState): The current game state.

        Raises:
            MethodNotImplementedError: If the method is not implemented in the derived class.

        Returns:
            Action: The resulting action.
        """
        # TODO: check score ????
        return self.compute_action(current_state=current_state)

    @abstractmethod
    def compute_action(self, **kwargs) -> Action:
        """
        Should be dedicated to adversarial search.

        Args:
            **kwargs: Additional arguments.

        Raises:
            MethodNotImplementedError: If the method is not implemented in the derived class.

        Returns:
            Action: The action to play.
        """
        raise MethodNotImplementedError()

    def get_id(self) -> int:
        """
        Returns:
            int: The ID of the player.
        """
        return self.id

    def get_name(self) -> str:
        """
        Returns:
            str: The name of the player.
        """
        return self.name

    def __str__(self) -> str:
        """
        Returns a string representation of the Player object.

        Returns:
            str: The string representation.
        """
        return f"Player {self.get_name()} has ID {self.get_id()}."


class RemotePlayerProxy(EventSlave):
    """
    A class representing a remote player proxy.

    Attributes:
        mimics (type[Player]): The player type to mimic.
        sid: The session ID.
    """

    def __init__(self, mimics: type[Player], *args, **kwargs) -> None:
        """
        Initializes a new instance of the RemotePlayerProxy class.

        Args:
            mimics (type[Player]): The player type to mimic.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.mimics = mimics(*args, **kwargs)
        self.sid = None

    @remote_action("turn")
    def play(self, _: GameState) -> Action:
        """
        Plays a move.

        Args:
            _: The game state (ignored).

        Returns:
            Action: The action resulting from the move.
        """
        pass

    async def listen(self) -> Coroutine[Any, Any, None]:
        """
        Listens for events.

        Returns:
            Coroutine: A coroutine object.
        """
        self.sid = await EventMaster.get_instance().wait_for_identified_client(self.name)

    def activate(self) -> None:
        """
        Activates the remote player proxy.

        Raises:
            NotImplementedError: If the method is called on a remote EventSlave instance.
        """
        msg = "Trying to call activate on a remote EventSlave instance."
        raise NotImplementedError(msg)

    def __getattr__(self, attr):
        return getattr(self.mimics, attr)

    def __hash__(self) -> int:
        return self.sid

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)


class LocalPlayerProxy(EventSlave):
    """
    A class representing a local player proxy.

    Attributes:
        wrapped_player (Player): The wrapped player object.

    Methods:
        play(current_state: GameState) -> Action: Plays a move.
    """

    def __init__(self, wrapped_player: Player) -> None:
        """
        Initializes a new instance of the LocalPlayerProxy class.

        Args:
            wrapped_player (Player): The player object to wrap.
        """
        self.wrapped_player = wrapped_player
        self.activate(self.wrapped_player.name)

    @event_emitting("play")
    def play(self, current_state: GameState) -> Action:
        """
        Plays a move.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The action resulting from the move.
        """
        return self.compute_action(current_state=current_state)

    def __getattr__(self, attr):
        return getattr(self.wrapped_player, attr)

    def __hash__(self) -> int:
        return hash(self.wrapped_player)

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        return f"Player {self.wrapped_player.get_name()} has ID {self.wrapped_player.get_id()}."
