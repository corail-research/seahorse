import asyncio
import time

from aioprocessing import AioEvent, AioProcess, AioQueue
from aioprocessing.locks import AioEvent as Event
from aioprocessing.process import AioProcess as Process
from aioprocessing.queues import AioQueue as Queue

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


def container_player_loop(player: Player, in_queue: Queue, out_queue: Queue,
                          wait: Event, close: Event):
    while True:
        wait.wait()
        if close.is_set():
            break

        game_state, remaining_time, kwargs = in_queue.get()
        start = time.time()
        action = player.compute_action(current_state=game_state, remaining_time=remaining_time,**kwargs)
        end = time.time()

        out_queue.put((action, end-start))

    # return player, action, end-start

class PlayerContainer(Serializable):
    def __init__(self, player: Player) -> None:
        self.contained_player = player
        self.in_queue: Queue = AioQueue()
        self.out_queue: Queue = AioQueue()
        self.close_event: Event = AioEvent()
        self.wait_event: Event = AioEvent()

        self.close_event.clear()
        self.wait_event.clear()

        self.process: Process = AioProcess(target=container_player_loop,
                                           args=(player, self.in_queue,
                                                 self.out_queue, self.wait_event, self.close_event))

        self.process.start()

    async def play(self, game_state: GameState, remaining_time: float, **kwargs) -> tuple[Action, float]:
        self.wait_event.set()
        try:
            await self.in_queue.coro_put((game_state, remaining_time, kwargs))
            self.wait_event.clear()
            action, time_diff = await asyncio.wait_for(self.out_queue.coro_get(), timeout=remaining_time)
        except Exception as e:
            self.close_event.set()
            while not self.out_queue.empty():
                self.out_queue.get_nowait()
            self.close()
            raise e

        return action, time_diff

    def close(self) -> None:
        if self.process.is_alive():
            self.close_event.set()
            self.wait_event.set()


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
