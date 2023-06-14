from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Coroutine

from coliseum.game.action import Action
from coliseum.game.io_stream import EventMaster, EventSlave, event_emitting, remote_action
from coliseum.game.time_manager import TimeMixin
from coliseum.utils.custom_exceptions import MethodNotImplementedError


if TYPE_CHECKING:
    from coliseum.game.game_state import GameState


class Player(TimeMixin):
    """
    Attributes:
        obs (Representation): representation of the game
        id_player (int): id of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    next_id = 0

    def __init__(self, name: str = "bob", time_limit=1e6) -> None:
        self.id_player = Player.next_id
        self.name = name
        Player.next_id += 1
        self.init_timer(time_limit)

    def play(self, current_state: GameState) -> Action:
        """
        Implements the player's logic, calls solve with minimal informations
        Given the problem statement one might override this to add some information
        in the solve call.

        Args:
            current_state (GameState): the current game state

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Action: The action resulting
        """
        # TODO : check score ????
        return self.solve(current_state=current_state)

    @abstractmethod
    def solve(self, **kwargs) -> Action:
        """
        Should be dedicated to adversarial search

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Action: the action to play
        """
        raise MethodNotImplementedError()

    def get_id(self):
        """
        Returns:
            int: id_player
        """
        return self.id_player

    def get_name(self):
        """
        Returns:
            str: name
        """
        return self.name

    def __str__(self) -> str:
        return f"Player {self.get_name()} has ID {self.get_id()}."

class RemotePlayerProxy(EventSlave):

    def __init__(self,mimics:type[Player],name:str="RemotePlayer",*args,**kwargs) -> None:
        self.mimics = mimics(name=name,*args,**kwargs)
        self.sid = None

    @remote_action("turn")
    def play(self, _: GameState) -> Action:
        pass
    
    async def listen(self) -> Coroutine[Any, Any, None]:
        self.sid = await EventMaster.get_instance().wait_for_identified_client(self.name)

    def activate(self) -> None:
        raise NotImplementedError("Trying to call activate on a remote EventSlave instance.")

    def __getattr__(self,attr):
        return getattr(self.mimics,attr)

class LocalPlayerProxy(EventSlave):

    def __init__(self, wrapped_player:Player) -> None:
        self.wrapped_player = wrapped_player
        self.activate(self.wrapped_player.name)

    @event_emitting("play")
    def play(self, current_state: GameState) -> Action:
        return self.solve(current_state=current_state)
    
    def __getattr__(self,attr):
        return getattr(self.wrapped_player,attr)
