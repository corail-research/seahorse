import json
from argparse import Action
from typing import Any, Coroutine, Type

from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster, EventSlave, event_emitting, remote_action
from seahorse.player.player import Player
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
        self.sid = None

    @remote_action("turn")
    def play(self, *,current_state: GameState) -> Action:
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
        Listens for events.

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

    def __init__(self, wrapped_player: Player, masterless:bool=False, gs:Type=GameState) -> None:
        """
        Initializes a new instance of the LocalPlayerProxy class.

        Args:
            wrapped_player (Player): The player object to wrap.
            masterless (bool): True when the player is connected to a remote master.
        """
        self.wrapped_player = wrapped_player
        self.activate(self.wrapped_player.name,masterless=masterless,wrapped_id=wrapped_player.get_id())
        @self.sio.on("turn")
        async def handle_turn(*data):
            print("turn")
            print(data)
            print(gs.from_json(data[0],next_player=self))
            action = await self.play(gs.from_json(data[0],next_player=self))
            print("***",action)

        @self.sio.on("update_id")
        async def update_id(data):
            print("update_id received",json.loads(data)["new_id"])
            self.wrapped_player.id = json.loads(data)["new_id"]

    @event_emitting("action")
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

    def to_json(self) -> dict:
        return self.wrapped_player.to_json()
    
class InteractivePlayerProxy(LocalPlayerProxy):
    def __init__(self, mimics: type[Player], *args, **kwargs) -> None:
        super().__init__(mimics, *args, **kwargs)
        self.wrapped_player.player_type = "interactive"

    async def play(self, current_state: GameState) -> Action:
        while True:
            data = json.loads(await EventMaster.get_instance().wait_for_event("interact"))
            action = current_state.convert_light_action_to_action(data)
            if action in current_state.get_possible_actions():
                break
            else:
                await EventMaster.get_instance().sio.emit("ActionNotPermitted",None)
        return action
