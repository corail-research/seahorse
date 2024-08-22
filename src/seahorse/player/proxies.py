import json
import time

from typing import Any, Optional
from loguru import logger
from collections.abc import Coroutine

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster, EventSlave, event_emitting, remote_action
from seahorse.game.light_action import LightAction
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.gui_client import GUIClient
from seahorse.utils.serializer import Serializable


class RemotePlayerProxy(Serializable,EventSlave):
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
        self.activate(wrapped_id=self.mimics.get_id())
        self.id = self.mimics.id
        self.sid = None

    @remote_action("turn")
    def play(self, *,current_state: GameState, remaining_time: int) -> Action:
        """
        Plays a move.

        Args:
            current_state: The game state.

        Returns:
            Action: The action resulting from the move.
        """
        pass

    async def listen(self,**_) -> Coroutine[Any, Any, None]:
        """
        Fires up the listening process

        Returns:
            Coroutine: A coroutine object.
        """
        idmap = await EventMaster.get_instance().wait_for_identified_client(self.name,self.id)
        self.sid = idmap["sid"]

    def __getattr__(self, attr):
        return getattr(self.mimics, attr)

    def __hash__(self) -> int:
        return hash(self.sid)

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def to_json(self) -> str:
        return str(self.wrapped_id)


class LocalPlayerProxy(Serializable,EventSlave):
    """
    A class representing a local player proxy.

    Attributes:
        wrapped_player (Player): The wrapped player object.

    Methods:
        play(current_state: GameState) -> Action: Plays a move.
    """

    def __init__(self, wrapped_player: Player,gs:type=GameState) -> None:
        """
        Initializes a new instance of the LocalPlayerProxy class.

        Args:
            wrapped_player (Player): The player object to wrap.
        """
        self.wrapped_player = wrapped_player
        self.activate(self.wrapped_player.name,wrapped_id=wrapped_player.get_id())
        @self.sio.on("turn")
        async def handle_turn(*data):
            logger.info(f"{self.wrapped_player.name} is playing")
            logger.debug(f"Data received : {data}")
            deserialized = json.loads(data[0])
            logger.debug(f"Deserialized data : \n{deserialized}")
            action = await self.play(gs.from_json(data[0],next_player=self),remaining_time = deserialized["remaining_time"])
            logger.info(f"{self.wrapped_player} played the following action : \n{action}")

        @self.sio.on("update_id")
        async def update_id(data):
            logger.debug("update_id received",json.loads(data)["new_id"])
            self.wrapped_player.id = json.loads(data)["new_id"]

    @event_emitting("action")
    def play(self, current_state: GameState, remaining_time: int) -> Action:
        """
        Plays a move.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The action resulting from the move.
        """
        return self.compute_action(current_state=current_state, remaining_time=remaining_time).get_heavy_action(current_state)

    def __getattr__(self, attr):
        return getattr(self.wrapped_player, attr)

    def __hash__(self) -> int:
        return hash(self.wrapped_player)

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        return f"Player {self.wrapped_player.get_name()} (ID: {self.wrapped_player.get_id()})."

    def to_json(self) -> dict:
        return self.wrapped_player.to_json()

class InteractivePlayerProxy(LocalPlayerProxy):
    """Proxy for interactive players,
       inherits from `LocalPlayerProxy`
    """
    def __init__(self, mimics: Player, gui_path:Optional[str]=None, *args, **kwargs) -> None:
        """

        Args:
            mimics (type[Player]): A wrapped player, the internal logic will be overridden by an interactive one
            gui_path (str, optional): If the interaction is supposed to happen on the host machine, provide a GUI path to start it up. Defaults to None.
        """
        super().__init__(mimics, *args, **kwargs)
        self.wrapped_player.player_type = "interactive"
        self.path = gui_path
        self.shared_sid = None
        self.sid = None

    async def play(self, current_state: GameState, **_) -> Action:
        if self.shared_sid and not self.sid:
            self.sid=self.shared_sid.sid
        while True:
            data_gui = json.loads(await EventMaster.get_instance().wait_for_event(self.sid,"interact",flush_until=time.time()))
            try:
                data = current_state.convert_gui_data_to_action_data(data_gui)
                action = LightAction(data).get_heavy_action(current_state)

            except MethodNotImplementedError:
                #TODO: handle this case
                action = Action.from_json(data)

            if action in current_state.get_possible_heavy_actions():
                break
            else:
                await EventMaster.get_instance().sio.emit("ActionNotPermitted",None)
        return action

    async def listen(self, master_address, *, keep_alive: bool) -> None:
        if not self.shared_sid:
            await super().listen(master_address, keep_alive=keep_alive)
            embedded_client = GUIClient(path=self.path)
            await embedded_client.listen()
            self.sid = embedded_client.sid

    def share_sid(self,proxy:"InteractivePlayerProxy"):
        self.shared_sid=proxy

