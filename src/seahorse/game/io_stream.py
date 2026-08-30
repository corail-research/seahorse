from __future__ import annotations

import asyncio
import json
import re
import time
from collections import deque
from collections.abc import Awaitable, Callable
from typing import Any

import dill
import socketio

from aiohttp import web
from loguru import logger

from seahorse.game.action import Action
from seahorse.game.game_state import GameState

class EventSlave:
    """
    Client-side listener for receiving game events and state updates.

    EventSlave acts as a WebSocket client
    that connects to an [EventMaster][..EventMaster]
    server to receive real-time game state updates and send player actions.
    It's typically used by Player proxies to communicate with the game server.

    Typical Usage:
        - Instantiated by [Proxy][....player.proxies] classes
        - Connected to [EventMaster][..EventMaster] during game setup
        - Used to receive [game states][...game_state.GameState]
          and/or send computed actions

    Attributes:
        sio (socketio.AsyncClient): Underlying Socket.IO client instance.
        connected (bool): Whether the slave is currently connected to a master.
        identifier (str): Unique identifier for this slave instance.
        instance_id (int): Python native id associated with this instance.
        disconnected_cb (Callable | None):
            Callback function invoked on disconnect.
    """

    def activate(self,
                 identifier: str | None = None,
                 instance_id: int | None = None,
                 *,
                 disconnected_cb: Callable[[None], None] | None = None
                 ) -> None:
        """
        Initializes and configures the EventSlave for connection.

        Sets up the client with event handlers and prepares
        for connection to an EventMaster server.

        Args:
            identifier (str | None): Unique string identifier for this slave.
                Used by the master to identify this client. Must be provided
                unless instance_id is given.
            instance_id (int | None):
                Python native id of an associated instance.
                Used as an alternative to string identifier. Must be provided
                unless identifier is given.
            disconnected_cb (Callable | None):
                Optional callback function
                to be called when the connection is lost.
                Receives no arguments.

        Raises:
            ValueError: If neither identifier nor instance_id is provided.

        Note:
            Only one of identifier or instance_id needs to be provided.
            If identifier is not provided,
            uses `str(instance_id)` as identifier.
            Must be called before [listen()][..listen].
        """
        if identifier is None and instance_id is None:
            msg = "At least a string identifier \
            or an instance id should be provided for activation."
            raise ValueError(msg)

        self.sio = socketio.AsyncClient()
        self.connected = False

        if identifier is not None:
            self.identifier = identifier
        else:
            self.identifier = str(instance_id)

        if instance_id is not None:
            self.instance_id = instance_id
        else:
            self.instance_id = hash(identifier)

        self.disconnected_cb = disconnected_cb

        @self.sio.event()
        async def connect():
            self.connected = True
            if self.identifier is not None:
                await self.sio.emit("identify",
                                    json.dumps(self.__dict__,
                                               default=lambda _: "_"))

        @self.sio.event
        def disconnect():
            self.connected = False

    async def listen(self, master_address: str, *, keep_alive: bool) -> None:
        """
        Connects to the master server and starts listening for events.

        Args:
            master_address (str): WebSocket URL of the
                [EventMaster][...EventMaster] server
                (e.g., "http://localhost:8080").
            keep_alive (bool): Whether to keep the asyncio process alive.

                - True: Runs indefinitely, useful for standalone processes
                - False: Returns after connection, useful for managed contexts

        Note:
            Sends identification message to EventMaster upon connection.
        """
        if not self.connected:
            await self.sio.connect(master_address)
        if keep_alive:
            while self.connected:
                await asyncio.sleep(.1)

    async def close_connection(self) -> None:
        """
        Gracefully closes the connection to the master.

        Note:
            Waits briefly before disconnecting to allow pending messages.
        """
        await asyncio.sleep(.1)
        if hasattr(self, "connected") and self.connected:
            await self.sio.disconnect()
            self.connected = False


class EventMaster:
    """
    Singleton server that manages WebSocket connections for game events.

    EventMaster serves as the central communication hub for game sessions:
        - Broadcasts game state updates to all connected clients
        - Receives player actions from PlayerProxy clients
        - Manages client connections and identification
        - Coordinates game flow and event timing

    Singleton Pattern:
        Only one instance exists per process to avoid
        port conflicts and ensure consistent state management.

    Key Features:
        1. **WebSocket Server**: Hosts server for real-time communication
        2. **Client Management**: Tracks connected clients and their identities
        3. **Event Routing**: Routes game events between GameMaster and clients
        4. **State Synchronization**:
            Ensures all clients receive game state updates

    Attributes:
        expected_clients (int): Number of clients expected to connect.
        port (int): TCP port the server listens on.
        hostname (str): Hostname or IP address for the server.
        sio (socketio.AsyncServer): Underlying Socket.IO server instance.
        app (web.Application): aiohttp web application.
        event_loop (asyncio.AbstractEventLoop):
            Event loop for async operations.
        runner (web.AppRunner): aiohttp application runner.
    """

    _instance = None

    @staticmethod
    def get_instance(game_state: type[GameState] = GameState, port: int = 8080,
                     hostname: str = "localhost") -> EventMaster:
        """
        Singleton accessor for EventMaster instance.

        Args:
            game_state (type[GameState]):
                GameState class used for deserialization.
            port (int): TCP port to listen on. Defaults to 8080.
            hostname (str): Hostname or IP address to bind to.
                Defaults to "localhost".

        Returns:
            EventMaster: The singleton instance.

        Note:
            - First call creates the instance with given parameters
            - Subsequent calls ignore parameters
            - Ensures single WebSocket server per process
        """
        if EventMaster._instance is None:
            return EventMaster(game_state=game_state,
                               port=port, hostname=hostname)
        return EventMaster._instance

    def __init__(self, game_state: type[GameState], port: int, hostname: str):
        """
        Private constructor - use get_instance() instead.

        Args:
            game_state (type[GameState]): GameState class for deserialization.
            port (int): TCP port to listen on.
            hostname (str): Hostname or IP address to bind to.

        Raises:
            NotImplementedError: If instance already exists.
        """

        if EventMaster._instance is not None:
            msg = ("Trying to initialize multiple instances of EventMaster, "
                   "this is forbidden to avoid side-effects.\n"
                   "Call EventMaster.get_instance() instead.")
            raise NotImplementedError(msg)
        else:
            # Initializing attributes
            self.expected_clients = 0
            self._n_clients_connected = 0
            self._identified_clients = {}
            self._open_sessions = set()
            self._ident2sid = {}
            self._sid2ident = {}
            self._events = {}
            self._game_state = game_state
            self.port = port
            self.hostname = hostname

            # Standard python-socketio server
            self.sio = socketio.AsyncServer(async_mode="aiohttp",
                                            async_handlers=True,
                                            cors_allowed_origins="*",
                                            ping_timeout=1e6)
            self.app = web.Application()

            # Starting asyncio stuff
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)

            # Attaching the app
            self.sio.attach(self.app)

            self.runner = web.AppRunner(self.app)

            # Shutdown callback
            async def on_shutdown(_):
                for x in list(self._open_sessions):
                    if x in self._open_sessions:
                        await self.sio.disconnect(x)

            self.app.on_shutdown.append(on_shutdown)

            @self.sio.event()
            def connect(sid: str, *_):
                """
                Handles incoming WebSocket connections.

                Args:
                    sid (str): Socket.IO session ID of connecting client.
                """
                # TODO: Should we stop accept connect once we have all the expected clients?
                self._open_sessions.add(sid)
                self._n_clients_connected += 1
                logger.info(
                    f"Waiting for listeners {self._n_clients_connected} \
                    out of {self.expected_clients} are connected.")

            @self.sio.event
            def disconnect(sid: str):
                """
                Handles client disconnections.

                Args:
                    sid (str): Socket.IO session ID of disconnected client.
                """
                logger.warning(f"Lost connection: {sid}")
                self._n_clients_connected -= 1
                self._open_sessions.remove(sid)
                if (sid in self._sid2ident.keys() and
                        self._sid2ident[sid] in self._identified_clients):
                    logger.warning(
                        f"Client identified as \
                        {self._sid2ident[sid]} was lost.")
                    del self._identified_clients[self._sid2ident[sid]]

            @self.sio.on("*")
            async def catch_all(event: str, sid: str, data: Any):
                """
                Catches all events for debugging and logging.

                Args:
                    event (str): Event name.
                    sid (str): Session ID.
                    data (Any): Event data.
                """
                self._events[sid] = self._events.get(sid, {})
                self._events[sid][event] = self._events[sid].get(event,
                                                                 deque())
                self._events[sid][event].appendleft((time.time(), data))

            @self.sio.on("action")
            async def handle_play(sid: str, action: Action, elapsed: float):
                """
                Handles incoming player actions.

                Args:
                    sid (str): Session ID of the client sending the action.
                    action (Action): Action data from the client.
                    time (float): Elapsed time reported by the client.
                """
                # TODO : cope with race condition "action" before "identify"
                try:
                    self._identified_clients[self._sid2ident[sid]]["incoming"]\
                            .appendleft((action, elapsed))
                # Plainly throw away packets from disconnected clients
                except KeyError:
                    pass

            @self.sio.on("identify")
            async def handle_identify(sid: str, data: str):
                """
                Handles client identification.

                Args:
                    sid (str): Session ID of the identifying client.
                    data (str): JSON string containing identification data.
                """
                logger.info("Identifying a listener")
                logger.info(json.loads(data).get("identifier", 0))
                logger.debug(f"Deserialized data {json.loads(data)}")
                data = json.loads(data)

                # TODO: check presence of "id" in data
                idf = data.get("identifier", 0)
                reg = r"^"+idf+r"(_duplicate_[0-9]+$|$)"
                if list(filter(lambda x: re.search(reg, x),
                               self._ident2sid.keys())):
                    logger.warning(
                        "Two clients are using the same identifier, \
                        one of those will be ignored.")
                    idf = idf+"_duplicate_"+str(time.time())

                self._ident2sid[idf] = sid
                self._sid2ident[sid] = idf
                self._identified_clients[idf] = {
                    "sid": sid,
                    "id": data.get("instance_id", None),
                    "incoming": deque(),
                    "attached": False
                }

            # Setting the singleton instance
            EventMaster._instance = self

    async def wait_for_next_play(self, sid: str) -> tuple[Action, float]:
        """
        Waits for a specific client to send their action.

        This is a blocking coroutine that waits
        until the specified client sends an "action" event.

        Args:
            sid (str): Session ID of the client to wait for.

        Returns:
            The received action as a [StatefulAction][....stateful_action.StatefulAction]

            Time difference (computation time) from the client
        """
        # TODO: revise sanity checks to avoid critical errors
        # TODO: this force to emit a statefull action, it should be rework to accept all action types
        logger.info(f"Waiting for next play from {self._sid2ident[sid]}")
        while not len(self._identified_clients[self._sid2ident[sid]]["incoming"]):
            await asyncio.sleep(.1)
        logger.info("Action received")
        action_json, time_diff = self._identified_clients[self._sid2ident[sid]]["incoming"].pop()
        if isinstance(action_json, str):
            action_json = json.loads(action_json)

        action_type = dill.loads(action_json["__action_type__"])
        action = action_type.from_json(action_json)

        return action, time_diff

    async def wait_for_event(self, sid: str, label: str, *,
                             flush_until: float | None = None) -> str | None:
        """
        Waits for a specific event from a client with a blocking coroutine.

        Args:
            sid (int): Session ID of the client to wait for.
            label (str): Event name/label to wait for.
            flush_until (float | None): Timestamp threshold for ignoring
                old events. Events older than this timestamp are discarded.
                If None, uses the first available event.

        Returns:
            The event data as a string, None if no matching event was found (after flushing).

        Note:
            Stale events can be filtered out using `flush_until`
        """
        while not len(self._events.get(sid, {}).get(label, [])):
            await asyncio.sleep(.1)
        ts, data = self._events[sid][label].pop()

        if (not flush_until) or ts >= flush_until:
            return data
        else:
            await self.wait_for_event(sid, label, flush_until=flush_until)

    # TODO: Maybe should be called "wait_for_client_identification" instead
    async def wait_for_identified_client(self, name: str, local_id: int) -> dict[str, Any]:
        """
        Waits for a client to identify themselves and attaches them.

        Args:
            name (str): Expected identifier name of the client.
            local_id (int): Local player ID to assign to the client.

        Returns:
            Client information dictionary containing:

                - `"sid"`: Session ID
                - `"id"`: Client's local instance ID
                - `"incoming"`: Deque of pending actions
                - `"attached"`: Attachment status

        Note:
            - Blocks until a client with matching name identifies
            - Marks client as attached to prevent reuse
            - Sends `"update_id"` event to sync client with local player ID
            - Used during game setup to connect
              [player proxies][.....player.proxies]
        """
        reg = r"^"+name+r"([0-9]+$|$)"

        def unattached_match(x):
            return (re.search(reg, x)
                    and not self._identified_clients[x]["attached"])

        matching_names = list(filter(unattached_match,
                                     self._ident2sid.keys()))
        while not matching_names:
            await asyncio.sleep(.1)
            matching_names = list(filter(unattached_match,
                                         self._ident2sid.keys()))

        cl = self._identified_clients[matching_names[0]]
        self._identified_clients[matching_names[0]]["attached"] = True

        await self.sio.emit("update_id",
                            json.dumps({"new_id": local_id}),
                            to=cl["sid"])
        return cl

    def start(self, task: Callable[[None], None], listeners: list[EventSlave],
              close_cb: Callable[[], Awaitable] | None = None) -> None:
        """
        Starts the EventMaster server and runs the game task.

        Blocking method procedure:
            1. Starts the WebSocket server
            2. Waits for all listeners to connect
            3. Executes the game task
               (typically [play_game][....master.GameMaster.play_game])
            4. Cleans up connections and resources

        Args:
            task (Callable[[None], None]): Async function to run as the main
                game task. Typically GameMaster.play_game() or similar.
            listeners (list[EventSlave]): List of EventSlave instances that
                will connect to this server (players and spectators).
            close_cb (Callable[[], Awaitable] | None): Optional callback
                to execute after game completion, for cleanup.
        """
        slaves = list(filter(lambda x: isinstance(x, EventSlave), listeners))
        self.expected_clients = len(slaves)

        # Sets the runner up and starts the tcp server
        self.event_loop.run_until_complete(self.runner.setup())
        site = web.TCPSite(self.runner, self.hostname, self.port)
        self.event_loop.run_until_complete(site.start())

        async def stop(task):
            # Waiting for all listeners to connect
            logger.info(f"Waiting for listeners {self._n_clients_connected} "
                        f"out of {self.expected_clients} are connected.")
            for x in slaves:
                # TODO: keep_alive should probably not always be False
                # or the parameter should be removed
                await x.listen(
                    master_address=f"http://{self.hostname}:{self.port!s}",
                    keep_alive=False)

            # Launching the task
            logger.info("Starting match")
            task_future = self.sio.start_background_task(task)

            # Await the game task completion
            try:
                await task_future
            except asyncio.CancelledError:
                logger.warning("Game task was cancelled.")

            # Close listeners connection
            for x in slaves:
                await x.close_connection()

            logger.debug(
                "Canceling pending tasks related to disconnected clients.")
            all_pending_tasks = [
                task for task in asyncio.all_tasks()
                if task is not asyncio.current_task()
            ]

            for pending_task in all_pending_tasks:
                try:
                    pending_task.cancel()
                except asyncio.CancelledError:
                    pass

            # Cleanup runner to release socket
            await self.runner.cleanup()

            if close_cb is not None:
                await close_cb()

        # Blocking call to the procedure
        self.event_loop.run_until_complete(stop(task))
