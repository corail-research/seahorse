import asyncio
import time

from aioprocessing import AioManager, AioProcess
from aioprocessing.managers import AioSyncManager as Manager
from aioprocessing.process import AioProcess as Process
from aioprocessing.queues import AioQueue as Queue

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


def container_player_loop(player: Player, in_queue: Queue, out_queue: Queue):
    while True:
        in_value = in_queue.get()
        if in_value is None:
            break
        current_state, remaining_time, kwargs = in_value
        start = time.time()
        action = player.compute_action(current_state=current_state, remaining_time=remaining_time,**kwargs)
        end = time.time()

        out_queue.put((action, end-start))

    # return player, action, end-start

class PlayerContainer(Serializable):
    def __init__(self, player: Player) -> None:
        self.contained_player = player
        self.manager: Manager = AioManager()
        self.in_queue: Queue = self.manager.AioQueue()
        self.out_queue: Queue = self.manager.AioQueue()
        self.closed = False

        self.process: Process = AioProcess(target=container_player_loop,
                                           daemon=True,
                                           args=(player, self.in_queue,
                                                 self.out_queue))

        self.process.start()

    async def play(self, current_state: GameState, remaining_time: float, **kwargs) -> tuple[Action, float]:
        try:
            await self.in_queue.coro_put((current_state, remaining_time, kwargs))
            action, time_diff = await asyncio.wait_for(self.out_queue.coro_get(), timeout=remaining_time)
        except Exception as e:
            while not self.out_queue.empty():
                self.out_queue.get_nowait()
            await self.close()
            raise e

        return action, time_diff

    async def close(self) -> None:
        if not self.closed:
            self.closed = True
            self.in_queue.put_nowait(None)
            await asyncio.sleep(.1)
            while not self.in_queue.empty():
                self.in_queue.get_nowait()
            self.manager.shutdown()


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
