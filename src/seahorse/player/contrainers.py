import asyncio
import time
from multiprocessing import Process, Queue
from typing import Any

from loguru import logger
from pebble import asynchronous

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


def container_player_loop(player: Player, game_state: GameState,
                          remaining_time: float, **kwargs) -> tuple[Player, Action, float]:
    start = time.time()
    action = player.compute_action(current_state=game_state, remaining_time=remaining_time,**kwargs)
    end = time.time()

    return player, action, end-start

class PlayerContainer(Serializable):
    def __init__(self, player: Player, gs:type[GameState]=GameState) -> None:
        self.contained_player = player
        # self.queue: Queue[GameState | Action | float | dict[str, Any]] = Queue()

        # self.process = Process(target=container_player_loop,
        #                        args=(player, self.queue, gs))
        # self.process.start()

    async def play(self, game_state: GameState, remaining_time: float, **kwargs) -> tuple[Action, float]:

        # This approach isn't the most efficient for general speedtime but it doesn't slow down the player computation.
        # TODO: find a way to spawn a process once and transmit the informations every turn.
        func = asynchronous.process(container_player_loop, timeout=remaining_time)
        player, action, time_diff = await func(self.contained_player, game_state, remaining_time, **kwargs)

        self.contained_player = player

        return action, time_diff

    def close(self) -> None:
        if self.process.is_alive():
            self.process.kill()
            self.process.close()
        self.queue.close()

    def get_player(self) -> Player:
        return self.contained_player

    def get_id(self) -> int:
        return self.contained_player.get_id()

    def get_name(self) -> str:
        return self.contained_player.get_name()

    def __getattr__(self, attr):
        return getattr(self.contained_player, attr)

    def __hash__(self) -> int:
        return hash(self.contained_player)

    def __eq__(self, __value: object) -> bool:
        return hash(self.contained_player) == hash(__value)

    def __str__(self) -> str:
        return str(self.contained_player)

    def to_json(self) -> dict:
        return self.contained_player.to_json()
