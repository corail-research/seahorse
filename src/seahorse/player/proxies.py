import functools
import json
import time
from abc import abstractmethod
from collections.abc import Coroutine
from typing import Callable, Optional

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

    @abstractmethod
    async def play(self, current_state: GameState, remaining_time: float, **kwargs) -> tuple[Action, float]:
        """
        Plays a move.

        Args:
            current_state: The game state.

        Returns:
            Action: The action resulting from the move.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise MethodNotImplementedError()

    @abstractmethod
    def to_player(self) -> Player:
        raise MethodNotImplementedError()

    @abstractmethod
    def get_id(self) -> int:
        raise MethodNotImplementedError()

    @abstractmethod
    def get_name(self) -> str:
        raise MethodNotImplementedError()

    @abstractmethod
    def __getattr__(self, attr):
        raise MethodNotImplementedError()

    @abstractmethod
    def __hash__(self) -> int:
        raise MethodNotImplementedError()

    @abstractmethod
    def __eq__(self, __value: object) -> bool:
        raise MethodNotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        raise MethodNotImplementedError()


class ContaineredPlayerProxy(PlayerProxy):

    def __init__(self, wrapped_player: Player) -> None:
        self.containered_player = PlayerContainer(wrapped_player)

    async def play(self, current_state: GameState, remaining_time: float, **kwargs) -> tuple[Action, float]:
        return await self.containered_player.play(current_state, remaining_time, **kwargs)

    async def close(self) -> None:
        await self.containered_player.close()

    def to_player(self) -> Player:
        return self.containered_player.get_player()

    def get_id(self):
        return self.containered_player.get_id()

    def get_name(self):
        return self.containered_player.get_name()

    def __getattr__(self, attr):
        return getattr(self.containered_player, attr)

    def __hash__(self) -> int:
        return hash(self.containered_player)

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        return str(self.containered_player)

    def to_json(self) -> dict:
        return self.containered_player.to_json()

class RemotePlayerProxy(PlayerProxy, EventSlave):
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
        self.mimic = mimics(*args, **kwargs)
        self.activate(instance_id=self.mimic.get_id())
        self.sid = None

    @staticmethod
    def remote_action(label: str):
        """Proxy decorator to override an expected local behavior with a distant one
        *The logic in decorated function is ignored*
        Args:
            label (str): the time of event to emit to trigger the distant logic
        """
        def meta_wrapper(fun: Callable):
            @functools.wraps(fun)
            async def wrapper(self:"RemotePlayerProxy",current_state:GameState,
                              remaining_time:float,*_,**kwargs) -> tuple[Action,float]:
                if self.sid is None:
                    msg = f"Remote player {self} is not connected (SID missing)"
                    raise ValueError(msg)

                state_data = json.dumps({**current_state.to_json()},
                                  default=lambda x:x.to_json())
                await EventMaster.get_instance().sio.emit(label,(state_data, remaining_time, kwargs),to=self.sid)
                out = await EventMaster.get_instance().wait_for_next_play(self.sid,current_state.players)
                return out

            return wrapper

        return meta_wrapper

    @remote_action("turn")
    async def play(self, *,current_state: GameState, remaining_time: float, **kwargs) -> None:
        pass

    async def close(self) -> None:
        return await self.close_connection()

    async def listen(self,**_) -> None:
        """
        Fires up the listening process

        Returns:
            Coroutine: A coroutine object.
        """
        idmap = await EventMaster.get_instance().wait_for_identified_client(self.name,self.instance_id)
        self.sid = idmap["sid"]

    def to_player(self) -> Player:
        return self.mimic

    def get_id(self):
        return self.mimic.get_id()

    def get_name(self):
        return self.mimic.get_name()

    def __getattr__(self, attr):
        return getattr(self.mimic, attr)

    def __hash__(self) -> int:
        return hash(self.sid)

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        return f"Player {self.mimic.get_name()}({self.mimic.get_id()})."

    def to_json(self) -> str:
        return str(self.instance_id)


class LocalPlayerProxy(PlayerProxy, EventSlave):
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
        self.activate(self.wrapped_player.name,wrapped_player.get_id())
        @self.sio.on("turn")
        async def handle_turn(*data):
            logger.info(f"{self.wrapped_player.name} is playing")
            logger.debug(f"Data received : {data}")
            deserialized = json.loads(data[0])
            logger.debug(f"Deserialized data : \n{deserialized}")
            action, _ = await self.play(gs.from_json(data[0],active_player=self),
                                     remaining_time=data[1], kwargs=data[2])
            logger.info(f"{self.wrapped_player} played the following action : \n{action}")

        @self.sio.on("update_id")
        async def update_id(data):
            logger.debug("update_id received",json.loads(data)["new_id"])
            self.wrapped_player.id = json.loads(data)["new_id"]

    @staticmethod
    def event_emitting(label:str):
        """Decorator to also send the function's output trough listening socket connexions

        Args:
            label (str): the type of event to emit
        """
        def meta_wrapper(fun: Callable[...,Coroutine[None, None, tuple[Action,float]]]):
            @functools.wraps(fun)
            async def wrapper(self:EventSlave,*args,**kwargs):
                action, time_diff = await fun(self,*args, **kwargs)
                await self.sio.emit(label,(json.dumps(action.to_json(),default=lambda x:x.to_json()), time_diff))
                return (action, time_diff)

            return wrapper

        return meta_wrapper

    @event_emitting("action")
    async def play(self, current_state: GameState, remaining_time: float, **kwargs) -> tuple[Action, float]:
        """
        Plays a move.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The action resulting from the move.
        """

        start = time.time()
        action = self.wrapped_player.compute_action(current_state=current_state, remaining_time=remaining_time,**kwargs)
        end = time.time()

        return action.get_stateful_action(game_state=current_state), end-start

    async def close(self) -> None:
        return await self.close_connection()

    def to_player(self) -> Player:
        return self.wrapped_player

    def get_id(self):
        return self.wrapped_player.get_id()

    def get_name(self):
        return self.wrapped_player.get_name()

    def __getattr__(self, attr):
        return getattr(self.wrapped_player, attr)

    def __hash__(self) -> int:
        return hash(self.wrapped_player)

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __str__(self) -> str:
        return f"Player {self.wrapped_player.get_name()}({self.wrapped_player.get_id()})."

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
            gui_path (str, optional): If the interaction is supposed to happen on the host machine, provide a GUI path
                                      to start it up. Defaults to None.
        """
        super().__init__(mimics, *args, **kwargs)
        self.path = gui_path
        self.shared_sid = None
        self.sid = None

    async def play(self, current_state: GameState, **_) -> Action | Serializable:
        if self.shared_sid and not self.sid:
            self.sid=self.shared_sid.sid

        if self.sid is None:
                msg = f"Remote player {self} is not connected (SID missing)"
                raise ValueError(msg)

        while True:
            response = await EventMaster.get_instance().wait_for_event(self.sid,"interact",flush_until=time.time())
            if response is None:
                msg = "No response from 'interact' event"
                raise ValueError(msg)

            data_gui = json.loads(response)
            try:
                data = current_state.convert_gui_data_to_action_data(data_gui)
                action = StatelessAction(data).get_stateful_action(current_state)

            except MethodNotImplementedError:
                #TODO: handle this case
                action = Action.from_json(data)

            if action in current_state.get_possible_stateful_actions():
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
