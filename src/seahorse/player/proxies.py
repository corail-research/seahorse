import functools
import json
import time
from abc import abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any

from loguru import logger

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster, EventSlave
from seahorse.game.stateless_action import StatelessAction
from seahorse.player.contrainers import PlayerContainer
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.gui_client import GUIClient
from seahorse.utils.serializer import Serializable


class PlayerProxy(Serializable):
    """
    Abstract base class for player proxies that handle player interactions.

    This class defines the interface for different types of player proxies that
    manage how players interact with the game system.
    Each proxy type implements a specific communication
    pattern while maintaining a consistent interface for the game engine.

    Proxies handle the delegation of action computation, whether it's performed
    locally, in a separate process, on a remote server, or through interactive
    user input. They also manage connection lifecycle and resource cleanup.

    Subclasses must implement all abstract methods to provide specific proxy
    functionality.
    """

    @abstractmethod
    async def play(self, current_state: GameState,
                   remaining_time: float, **kwargs) -> tuple[Action, float]:
        """
        Plays a move asynchronously
        by requesting an action from the proxied player.

        Args:
            current_state (GameState):
                The current game state.
            remaining_time (float):
                The remaining time (in seconds) for the move.
            **kwargs (dict[str, _]):
                Additional keyword arguments
                for the player's compute_action method.

        Returns:
            Action: The chosen game action
                that will be applied to the game state
            float: The time (in seconds)
                taken by the player to compute the action

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        """
        Closes the proxy and cleans up any resources.

        This method should perform proper cleanup of any connections,
        processes, or resources used by the proxy.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def to_player(self) -> Player:
        """
        Retrieves the underlying Player object.

        Returns:
            Player: The actual player instance being proxied.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def get_id(self) -> int:
        """
        Retrieves the player's unique identifier.

        Returns:
            int: The player's ID.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def get_name(self) -> str:
        """
        Retrieves the player's name.

        Returns:
            str: The player's name.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def __getattr__(self, attr) -> Any:
        """
        Delegates attribute access to the underlying player.

        Args:
            attr (str): The attribute name to access.

        Returns:
            Any: The attribute value from the underlying player.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def __hash__(self) -> int:
        """
        Retrieves a hash value for the proxy.

        Returns:
            int: Hash value based on the underlying player.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def __eq__(self, __value: object) -> bool:
        """
        Compares this proxy with another object for equality.

        Args:
            __value (object): The object to compare with.

        Returns:
            bool: True if the proxies are considered equal.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """

        raise MethodNotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        """Returns a string representation of the proxy.

        Returns:
            str: String representation of the player proxy.

        Raises:
            MethodNotImplementedError: If not implemented by subclass.
        """
        raise MethodNotImplementedError()


class ContaineredPlayerProxy(PlayerProxy):
    """
    Proxy for players running in separate processes via PlayerContainer.

    This proxy wraps a PlayerContainer to handle players running in isolated
    processes. It's particularly useful for enforcing time limits on
    player computations and isolating memory usage between players.

    The PlayerContainer runs the player's compute_action method
    in a separate Python process, communicating through multiprocessing queues.

    Attributes:
        containered_player (PlayerContainer):
            The container managing the player process
            and inter-process communication.
    """

    def __init__(self, wrapped_player: Player, gs: type[GameState]) -> None:
        """
        Initializes the ContaineredPlayerProxy.

        Args:
            wrapped_player (Player): The player instance to containerize.
        """
        self.containered_player = PlayerContainer(wrapped_player, gs=gs)

    async def play(self, current_state: GameState,
                   remaining_time: float, **kwargs) -> tuple[Action, float]:
        """
        Requests an action from the containerized player
        with timeout enforcement.

        Args:
            current_state (GameState):
                The current game state.
            remaining_time (float):
                The remaining time (in seconds) for the move.
            **kwargs (dict[str, _]):
                Additional keyword arguments
                for the player's compute_action method.

        Returns:
            Action: The chosen game action
                that will be applied to the game state.
            float: The time (in seconds)
                taken by the player to compute the action.

        Raises:
            TimeoutError: If the player process exceeds remaining_time.
            BrokenPipeError: If the inter-process communication fails.
            RuntimeError:
                If the player process crashes or becomes unresponsive.
        """
        return await self.containered_player.play(current_state,
                                                  remaining_time,
                                                  **kwargs)

    async def close(self) -> None:
        """Closes the container and cleans up the process."""
        await self.containered_player.close()

    def to_player(self) -> Player:
        """
        Retrieves the underlying Player instance.

        Returns:
            Player: The player being containerized.
        """
        return self.containered_player.get_player()

    def get_id(self) -> int:
        """
        Retrieves the player's ID.

        Returns:
            int: The player's unique identifier.
        """
        return self.containered_player.get_id()

    def get_name(self) -> str:
        """
        Retrieves the player's name.

        Returns:
            str: The player's name.
        """
        return self.containered_player.get_name()

    def __getattr__(self, attr) -> Any:
        """
        Delegates attribute access to the containerized player.

        Args:
            attr (str): The attribute name to access.

        Returns:
            Any: The attribute value from the containerized player.
        """
        return getattr(self.containered_player, attr)

    def __hash__(self) -> int:
        """
        Retrieves the containerized player hash value.

        Returns:
            int: Hash value of the containerized player.
        """
        return hash(self.containered_player)

    def __eq__(self, __value: object) -> bool:
        """
        Compares this proxy with another for equality.

        Args:
            __value (object): The object to compare with.

        Returns:
            bool: True if both objects have the same hash value.
        """
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        """
        Returns a string representation of the containerized player.

        Returns:
            str: String representation of the containerized player.
        """
        return str(self.containered_player)

    def to_json(self) -> dict:
        """
        Serializes the containerized player to JSON format.

        Returns:
            dict: JSON-serializable dictionary representation.
        """
        return self.containered_player.to_json()


class RemotePlayerProxy(PlayerProxy, EventSlave):
    """
    A proxy for players running on remote systems.

    This proxy enables gameplay across network boundaries by communicating
    game states to remote players and receiving their actions through web
    sockets.

    Attributes:
        mimic (Player):
            A local player instance used for metadata (name, ID)
            and serialization, while actual computation happens remotely.
        sid (str | None):
            The session ID for the remote connection,
            None until the remote player connects.
    """

    def __init__(self, mimics: type[Player], *args, **kwargs) -> None:
        """
        Initializes a RemotePlayerProxy that mimics
        a player type for remote play.

        Args:
            mimics (type[Player]):
                The player class to mimic for metadata purposes.
                An instance is created locally to maintain player
                identity and serialization format.
            *args (tuple[_, ...]):
                Positional arguments to pass to the player constructor.
            **kwargs (dict[str, _]):
                Keyword arguments to pass to the player constructor.
        """
        self.mimic = mimics(*args, **kwargs)
        self.activate(instance_id=self.mimic.get_id())
        self.sid = None

    @staticmethod
    def remote_action(label: str):
        """
        Decorator factory for methods that should delegate to remote players.

        Creates a decorator that replaces local method logic
        with remote communication.
        The decorated method will emit an event to the remote player and
        wait for their response instead of executing local code.

        Args:
            label (str): The event name to emit (e.g., "turn", "move").
        """
        def meta_wrapper(fun: Callable):
            @functools.wraps(fun)
            async def wrapper(self: "RemotePlayerProxy",
                              current_state: GameState,
                              remaining_time: float,
                              *_, **kwargs) -> tuple[Action, float]:
                if self.sid is None:
                    msg = f"Remote player {self} \
                            is not connected (SID missing)"
                    raise ValueError(msg)

                state_data = json.dumps({**current_state.to_json()},
                                        default=lambda x: x.to_json())
                emit_data = (state_data, remaining_time, kwargs)
                await EventMaster.get_instance().sio.emit(label, emit_data,
                                                          to=self.sid)
                out = await EventMaster.get_instance()\
                    .wait_for_next_play(self.sid)
                return out

            return wrapper

        return meta_wrapper

    @remote_action("turn")
    async def play(self, *, current_state: GameState,
                   remaining_time: float, **kwargs) -> None:
        """
        Requests an action from a remote player.

        This method is [a remote action][..remote_action], which means the
        local implementation is ignored.

        Args:
            current_state (GameState):
                The game state to send to the remote player.
            remaining_time (float):
                Time limit for the remote player's computation.
            **kwargs (dict[str, _]):
                Additional parameters for the remote player.

        Note:
            The `@remote_action("turn")` decorator ensure that
            the results are returned from the remote player response.
        """
        pass

    async def close(self) -> None:
        """
        Closes the connection to the remote player and cleans up resources.
        """
        return await self.close_connection()

    async def listen(self, **_) -> None:
        """
        Establishes the connection and waits for remote player identification.

        This method must be called before
        the remote player can receive game states.
        It registers with the EventMaster and
        waits for the remote player to connect and identify themselves.

        Raises:
            ConnectionError: If the connection cannot be established.
            TimeoutError:
                If the remote player doesn't connect within a reasonable time.
        """
        master = EventMaster.get_instance()
        idmap = await master.wait_for_identified_client(self.name,
                                                        self.instance_id)
        self.sid = idmap["sid"]

    def to_player(self) -> Player:
        """
        Retrieves the local mimic Player instance for serialization.

        Returns:
            Player:
                The local player instance used for metadata and serialization.
        """
        return self.mimic

    def get_id(self) -> int:
        """
        Retrieves the player ID from the mimic instance.

        Returns:
            int: The player's unique identifier.
        """
        return self.mimic.get_id()

    def get_name(self) -> str:
        """
        Retrieves the player name from the mimic instance.

        Returns:
            str: The player's display name.
        """
        return self.mimic.get_name()

    def __getattr__(self, attr) -> Any:
        """
        Delegates attribute access to the mimic player instance.

        Args:
            attr (str): The attribute name to access.

        Returns:
            Any: The attribute value from the mimic player.

        Raises:
            AttributeError: If the attribute doesn't exist on the mimic player.
        """
        return getattr(self.mimic, attr)

    def __hash__(self) -> int:
        """
        Retrieves a hash value based on the session ID.

        Returns:
            int: Hash of the session ID, or 0 if not yet connected.
        """
        return hash(self.sid)

    def __eq__(self, __value: object) -> bool:
        """
        Compares this proxy with another object for equality.

        Args:
            __value (object): The object to compare with this proxy.

        Returns:
            bool: True if both objects are RemotePlayerProxies with equal hash.
        """
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        """Returns a string representation of the remote player.

        Returns:
            str: String showing the player's name and ID.
        """
        return f"RemotePlayer {self.mimic.get_name()}({self.mimic.get_id()})."

    def to_json(self) -> str:
        """
        Serializes the proxy to JSON format.

        Returns:
            str: JSON string representation of the instance ID.
        """
        return str(self.instance_id)


class LocalPlayerProxy(PlayerProxy, EventSlave):
    """
    A proxy for local players that can also emit their actions.

    This proxy wraps a local player instance but adds event emission
    capability. This allows local players to broadcast their actions,
    which is useful for remote play.

    The proxy listens for "turn" events (which would come from a game master)
    and emits "action" events when the player makes a move.

    Attributes:
        wrapped_player (Player):
            The actual local player instance that computes actions.
    """

    def __init__(self, wrapped_player: Player,
                 gs: type[GameState] = GameState) -> None:
        """
        Initializes a LocalPlayerProxy with a local player and GameState type.

        Args:
            wrapped_player (Player):
                The local player instance to wrap and proxy.
            gs (type[GameState]):
                The GameState class used for deserializing
                incoming game states.
                Defaults to the base GameState class.
        """
        self.wrapped_player = wrapped_player
        self.activate(self.wrapped_player.name, wrapped_player.get_id())

        @self.sio.on("turn")
        async def handle_turn(*data):
            logger.info(f"{self.wrapped_player.name} is playing")
            logger.debug(f"Data received : {data}")
            deserialized = json.loads(data[0])
            logger.debug(f"Deserialized data : \n{deserialized}")
            action, _ = await self.play(gs.from_json(data[0], active_player=self),
                                        remaining_time=data[1], kwargs=data[2])
            logger.info(f"{self.wrapped_player} played the following action : \n{action}")

        @self.sio.on("update_id")
        async def update_id(data):
            logger.debug("update_id received", json.loads(data)["new_id"])
            self.wrapped_player.id = json.loads(data)["new_id"]

    @staticmethod
    def event_emitting(label: str):
        """
        Decorator factory for methods that should emit their results.

        Creates a decorator that wraps a method to emit its return value as a
        Socket.IO event after execution. This is useful for broadcasting player
        actions to spectators or recording systems.

        Args:
            label (str): The event name to emit (e.g., "action", "move").
        """
        def meta_wrapper(fun: Callable[..., Coroutine[None, None, tuple[Action, float]]]):
            @functools.wraps(fun)
            async def wrapper(self: EventSlave, *args, **kwargs):
                action, time_diff = await fun(self, *args, **kwargs)
                await self.sio.emit(label, (action.to_json(), time_diff))
                return (action, time_diff)

            return wrapper

        return meta_wrapper

    @event_emitting("action")
    async def play(self, current_state: GameState,
                   remaining_time: float, **kwargs) -> tuple[Action, float]:
        """
        Plays a move locally and [emits the action][..event_emitting].

        Args:
            current_state (GameState):
                The current game state.
            remaining_time (float):
                The remaining time (in seconds) for the move.
            **kwargs (dict[str, _]):
                Additional keyword arguments
                for the player's compute_action method.

        Returns:
            Action: The chosen game action
                that will be applied to the game state.
            float: The time (in seconds)
                taken by the player to compute the action.

        Note:
            The `@event_emitting("action")` decorator ensures
            the result is also broadcast to any connected listeners.
        """

        start = time.time()
        action = self.wrapped_player\
            .compute_action(current_state=current_state,
                            remaining_time=remaining_time,
                            **kwargs)
        end = time.time()

        return action.get_stateful_action(game_state=current_state), end-start

    async def close(self) -> None:
        """
        Closes the connection for this local proxy and free up resources.
        """
        return await self.close_connection()

    def to_player(self) -> Player:
        """
        Retrieves the wrapped local Player instance.

        Returns:
            Player: The original local player instance.
        """
        return self.wrapped_player

    def get_id(self) -> int:
        """
        Retrieves the ID of the wrapped player.

        Returns:
            int: The player's unique identifier.
        """
        return self.wrapped_player.get_id()

    def get_name(self) -> str:
        """
        Retrieves the name of the wrapped player.

        Returns:
            str: The player's display name.
        """
        return self.wrapped_player.get_name()

    def __getattr__(self, attr) -> Any:
        """Delegates attribute access to the wrapped player.

        Args:
            attr (str): The attribute name to access.

        Returns:
            Any: The attribute value from the wrapped player.

        Raises:
            AttributeError:
                If the attribute doesn't exist on the wrapped player.
        """
        return getattr(self.wrapped_player, attr)

    def __hash__(self) -> int:
        """
        Retrieves a hash value based on the wrapped player.

        Returns:
            int: Hash value of the wrapped player instance.
        """
        return hash(self.wrapped_player)

    def __eq__(self, __value: object) -> bool:
        """
        Compares this proxy with another object for equality.

        Two LocalPlayerProxies are considered equal if their wrapped players
        have the same hash value.

        Args:
            __value (object): The object to compare with this proxy.

        Returns:
            bool: True if both objects are LocalPlayerProxies with equal wrapped players.
        """
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        """
        Returns a string representation of the local player.

        Returns:
            str: String showing the player's name and ID.
        """
        return f"Player {self.wrapped_player.get_name()}({self.wrapped_player.get_id()})."

    def to_json(self) -> dict:
        """
        Serializes the proxy to JSON format using the player's serialization.

        Returns:
            dict: JSON-serializable dictionary representation of the wrapped player.
        """
        return self.wrapped_player.to_json()


class InteractivePlayerProxy(LocalPlayerProxy):
    """
    Proxy for interactive players that receive input
    from a graphical user interface.

    This proxy extends LocalPlayerProxy to support human players interacting
    through a GUI. Instead of using the wrapped player's compute_action method,
    it waits for user input from a web-based interface and validates the input
    against the current game state.

    Attributes:
        path (str | None):
            Path to a GUI application to launch on the host machine.
            If provided, the proxy will attempt to open this path
            (could be a URL or local file path) when the game starts.
        shared_sid (InteractivePlayerProxy | None):
            Another proxy instance to share a session ID with, useful for
            multiple GUI windows sharing the same connection.
        sid (str | None):
            The Socket.IO session ID for GUI communication,
            None until the GUI connects.
    """
    def __init__(self, mimics: Player, gui_path:str | None=None, *args, **kwargs) -> None:
        """
        Initializes an InteractivePlayerProxy for human players using a GUI.

        Args:
            mimics (Player):
                A player instance whose internal logic will be
                overridden by interactive input. The player is used
                for metadata (name, ID) but not for action computation.
            gui_path (str | None):
                If the interaction should happen via a local
                application, provide a path or URL to launch.
                This could be a web address (http://...),
                a local HTML file, or an application path.
                If None, assumes the GUI is already running.
            *args (tuple[_, ...]):
                Additional positional arguments
                passed to the parent constructor.
            **kwargs (dict[str, _]):
                Additional keyword arguments
                passed to the parent constructor.
        """
        super().__init__(mimics, *args, **kwargs)
        self.path = gui_path
        self.shared_sid = None
        self.sid = None

    async def play(self, current_state: GameState,
                   **_) -> tuple[Action | Serializable, float]:
        """
        Waits for interactive input from the GUI to determine the action.

        Args:
            current_state (GameState): The current game state to validate actions against.
            **_ (dict[str, _]): Ignored additional arguments (remaining_time is not used for interactive).

        Returns:
            tuple[Action | Serializable, float]:
                - The validated game action (or serializable alternative)
                - 0.0 (interactive play has no computation time limit)
        """
        if self.shared_sid and not self.sid:
            self.sid = self.shared_sid.sid

        if self.sid is None:
            msg = (f"Remote player {self} "
                   "is not connected (SID missing)")
            raise ValueError(msg)

        while True:
            master = EventMaster.get_instance()
            response = master.wait_for_event(self.sid,
                                             "interact",
                                             flush_until=time.time())
            if response is None:
                msg = "No response from 'interact' event"
                raise ValueError(msg)

            data_gui = json.loads(response)
            try:
                # TODO: Since we got StatelessAction now
                # GUI data could be directly put into it
                data = current_state.convert_gui_data_to_action_data(data_gui)
                action = StatelessAction(data)
                action = action.get_stateful_action(current_state)

            except MethodNotImplementedError:
                # TODO: handle this case
                action = Action.from_json(data)

            if action in current_state.get_possible_stateful_actions():
                break
            else:
                await master.sio.emit("ActionNotPermitted", None)

        return action, 0.0  # No time limit for interactive

    # TODO: Shouldn't the interactive player be always kept alive?
    async def listen(self, master_address: str, *, keep_alive: bool) -> None:
        """
        Sets up the interactive listener and launches the GUI if needed.

        Args:
            master_address (str):
                The address of the EventMaster server.
            keep_alive (bool):
                Whether to maintain the connection persistently.

        Note:
            If `shared_sid` is already set,
            this method skips creating a new GUI client,
            assuming another proxy already established the connection.
        """
        if not self.shared_sid:
            await super().listen(master_address, keep_alive=keep_alive)
            embedded_client = GUIClient(path=self.path)
            await embedded_client.listen()
            self.sid = embedded_client.sid

    def share_sid(self, proxy: "InteractivePlayerProxy"):
        """
        Shares the session ID with another InteractivePlayerProxy.

        This allows multiple interactive proxies
        to share a single GUI connection,
        which is useful when multiple human players
        are using the same interface.

        Args:
            proxy (InteractivePlayerProxy): Another proxy instance to share
                                            the session ID with.
        """
        self.shared_sid = proxy
