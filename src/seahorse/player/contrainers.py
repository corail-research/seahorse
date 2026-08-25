import asyncio
import time

from typing import Any
import dill

from aioprocessing import AioManager, AioProcess
from aioprocessing.managers import AioSyncManager as Manager
from aioprocessing.process import AioProcess as Process
from aioprocessing.queues import AioQueue as Queue

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


def container_player_loop(player: Player, in_queue: Queue,
                          out_queue: Queue, excpt_queue: Queue,
                          gs: type[GameState]):
    """
    Main loop for player processes running in separate containers.

    This function runs in a separate process
    and continuously listens for game states
    from the input queue, computes actions using the player's logic, and sends
    results back through the output queue.

    Args:
        player:
            The Player instance to compute actions.
        in_queue:
            Queue for receiving game state data from the main process.
        out_queue:
            Queue for sending computed actions
            and time back to the main process.
        excpt_queue:
            Queue for sending eventual exceptions.
        gs:
            Derived GameState type for the implemented game
    """
    try:
        while True:
            in_value = in_queue.get()
            if in_value is None:
                break
            current_state_json, remaining_time, kwargs = in_value
            current_state = gs.from_json(current_state_json)
            start = time.time()
            action = player.compute_action(
                current_state=current_state,
                remaining_time=remaining_time,
                **kwargs)
            end = time.time()

            out_queue.put((action.to_json(), end-start))
    except Exception as e:
        excpt_queue.put(e)
        out_queue.put((None, None))

class PlayerContainer(Serializable):
    """
    Container for running Player instances in separate processes.

    This class wraps a Player object and runs it in a separate process.
    This enable the proxy to interrupt the player
    computation if time limit is passed.
    It uses aioprocessing for asynchronous
    process management and communication.

    Attributes:
        contained_player (Player):
            The Player instance being wrapped.
        manager (Manager):
            AioManager for managing inter-process communication.
        in_queue (Queue):
            Queue for sending data to the player process.
        out_queue (Queue):
            Queue for receiving results from the player process.
        excpt_queue (Queue):
            Queue for receiving expections from the player process.
        closed (bool):
            Boolean indicating if the container has been closed.
        process (Process):
            The AioProcess instance running the player.

    Note:
        Attributes leverage the
        [aioprocessing](https://github.com/dano/aioprocessing) library,
        which provides async version of the blocking functions from
        the standard [multiprocessing][] objects.
    """

    def __init__(self, player: Player,
                 gs: type[GameState] = GameState) -> None:
        """
        Initializes the PlayerContainer with a player and starts the process.

        Args:
            player (Player): The Player instance to be containerized.
        """
        self.contained_player = player
        self.manager: Manager = AioManager()
        self.in_queue: Queue = self.manager.AioQueue()
        self.out_queue: Queue = self.manager.AioQueue()
        self.excpt_queue: Queue = self.manager.AioQueue()
        self.closed = False

        self.process: Process = AioProcess(target=container_player_loop,
                                           daemon=True,
                                           args=(player, self.in_queue,
                                                 self.out_queue,
                                                 self.excpt_queue,
                                                 gs))

        self.process.start()

    async def play(self, current_state: GameState,
                   remaining_time: float,
                   **kwargs) -> tuple[Action, float]:
        """
        Requests an action from the contained player.

        Args:
            current_state (GameState):
                The current game state to evaluate.
            remaining_time (float):
                The remaining time (in seconds) for the player.
            **kwargs (dict[str, _]):
                Additional arguments to pass to the player's
                compute_action method.

        Returns:
            Action: The chosen game action
                that will be applied to the game state
            float: The time (in seconds)
                taken by the player to compute the action

        Raises:
            Exception: If the player times out or encounters an error.
        """
        try:
            await self.in_queue.coro_put(
                    (current_state.to_json(), remaining_time, kwargs))
            action_json, time_diff = await asyncio.wait_for(
                    self.out_queue.coro_get(), timeout=remaining_time)
        except Exception as e:
            while not self.out_queue.empty():
                self.out_queue.get_nowait()
            await self.close()
            raise e

        if action_json is None or time_diff is None:
            e = await self.excpt_queue.coro_get()
            await self.close()
            raise e

        action_type = dill.loads(action_json["__action_type__"])
        return action_type.from_json(action_json), time_diff

    async def close(self) -> None:
        """
        Closes the player container and cleans up resources.

        Stops the player process, clears queues, and shuts down the manager.
        """
        if not self.closed:
            self.closed = True
            self.in_queue.put_nowait(None)
            await asyncio.sleep(.1)
            while not self.in_queue.empty():
                self.in_queue.get_nowait()
            self.manager.shutdown()

    def get_player(self) -> Player:
        """
        Retrieve the contained Player instance.

        Returns:
            Player: The original player object.

        Note:
            This [Player][] instance is a local proxy object,
            not the actual [Player][] instance running in the
            remote container process.
            **Attributes of this proxy are not synchronized
            with the remote instance during game execution.**
        """
        return self.contained_player

    def get_id(self) -> int:
        """
        Retrieves the ID of the contained player.

        Returns:
            int: The player's unique identifier.
        """
        return self.contained_player.get_id()

    def get_name(self) -> str:
        """
        Retrieves the name of the contained player.

        Returns:
            str: The player's name.
        """
        return self.contained_player.get_name()

    def __getattr__(self, attr) -> Any:
        """
        Delegates attribute access to the contained player.

        Args:
            attr (str): The attribute name to access.

        Returns:
            Any: The attribute value from the contained player.
        """
        return getattr(self.contained_player, attr)

    def __hash__(self) -> int:
        """
        Retrieves the hash of the contained player.

        Returns:
            int: Hash value based on the contained player.
        """
        return hash(self.contained_player)

    def __eq__(self, __value: object) -> bool:
        """
        Compares this container with another object for equality.

        Args:
            __value (object): The object to compare with.

        Returns:
            bool: True if both objects are PlayerContainers with equal players.
        """

        return hash(self.contained_player) == hash(__value)

    def __str__(self) -> str:
        """
        Retrieves the string representation of the contained player.

        Returns:
            str: String representation of the player.
        """
        return str(self.contained_player)

    def to_json(self) -> dict:
        """
        Serializes the contained player to JSON format.

        Returns:
            dict: JSON-serializable dictionary representation.
        """
        return self.contained_player.to_json()
