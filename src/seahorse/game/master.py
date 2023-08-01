import asyncio
import json
from abc import abstractmethod
from itertools import cycle
from typing import Dict, Iterable, List

from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import (
    ActionNotPermittedError,
    ColiseumTimeoutError,
    MethodNotImplementedError,
    StopAndStartError,
)


class GameMaster:
    """
    A class representing the game master.

    Attributes:
        name (str): The name of the game.
        initial_game_state (GameState): The initial state of the game.
        current_game_state (GameState): The current state of the game.
        players_iterator (Iterable): An iterable for the players, ordered according
            to the playing order. If a list is provided, a cyclic iterator is automatically built.
        log_file (str): The name of the log file.
    """

    def __init__(
        self, 
        name: str, 
        initial_game_state: GameState, 
        players_iterator: Iterable[Player], 
        log_file: str, 
        port: int =8080,
        hostname: str ="localhost",
        n_listeners: int =4
    ) -> None:
        """
        Initializes a new instance of the GameMaster class.

        Args:
            name (str): The name of the game.
            initial_game_state (GameState): The initial state of the game.
            players_iterator (Iterable[Player]): An iterable for the players, ordered according
                to the playing order.
            log_file (str): The name of the log file.
        """
        self.name = name
        self.current_game_state = initial_game_state
        self.initial_game_state = initial_game_state
        self.players = initial_game_state.players
        self.log_file = log_file
        self.players_iterator = cycle(players_iterator) if isinstance(players_iterator, list) else players_iterator
        next(self.players_iterator)
        self.emitter = EventMaster.get_instance(n_listeners,initial_game_state.__class__,port=port,hostname=hostname)

    async def step(self) -> GameState:
        """
        Calls the next player move.

        Returns:
            GamseState : The new game_state.
        """
        next_player = self.current_game_state.get_next_player()
        possible_actions = self.current_game_state.get_possible_actions()

        start = next_player.timer.start_timer()
        print("time :", next_player.timer._remaining_time)
        action = await next_player.play(self.current_game_state)
        next_player.timer.stop_timer()
        #print("time :", next_player.timer._remaining_time)
        if start != next_player.timer._last_timestamp :
            raise StopAndStartError()
        if next_player.timer.is_finished() :
            raise ColiseumTimeoutError()

        if action not in possible_actions:
            raise ActionNotPermittedError()

        return action.get_next_game_state()

    async def play_game(self) -> List[Player]:
        """
        Play the game.

        Returns:
            Iterable[Player]: The winner(s) of the game.
        """
        await self.emitter.sio.emit(
            "play",
            json.dumps(self.current_game_state.to_json(),default=lambda x:x.to_json()),
        )
        while not self.current_game_state.is_done():
            # TODO try except is illegal, need to identify the exception we need to catch probably Timeout

            self.current_game_state = await self.step()
            
            #except Exception:
                #temp_score = copy.copy(self.current_game_state.get_scores())
                #id_player_error = self.current_game_state.get_next_player().get_id()
                #temp_score.pop(id_player_error)
                #self.winner = self.compute_winner(temp_score)
                #self.current_game_state.get_scores()[id_player_error] = float(sys.maxsize)
                #return self.winner
            #print(self.current_game_state.get_rep())
            #print(self.current_game_state)
            await asyncio.sleep(.1)
            await self.emitter.sio.emit(
                "play",
                json.dumps(self.current_game_state.to_json(),default=lambda x:x.to_json()),
            )
        self.winner = self.compute_winner(self.current_game_state.get_scores())
        return self.winner

    def record_game(self) -> None:
        """
        Starts a game and broadcasts its successive states.
        """
        self.emitter.start(self.play_game, self.players)

    def update_log(self) -> None:
        """
        Updates the log file.

        Raises:
            MethodNotImplementedError: If the method is not implemented.
        """
        raise MethodNotImplementedError()

    def get_name(self) -> str:
        """
        Returns:
            str: The name of the game.
        """
        return self.name

    def get_game_state(self) -> GameState:
        """
        Returns:
            GameState: The current game state.
        """
        return self.current_game_state

    def get_json_path(self) -> str:
        """
        Returns:
            str: The path of the log file.
        """
        return self.log_file

    def get_winner(self) -> List[Player]:
        """
        Returns:
            Player: The winner(s) of the game.
        """
        return self.winner

    def get_scores(self) -> Dict[int, float]:
        """
        Returns:
            Dict: The scores of the current state.
        """
        return self.current_game_state.get_scores()

    @abstractmethod
    def compute_winner(self, scores: Dict[int, float]) -> List[Player]:
        """
        Computes the winner(s) of the game based on the scores.

        Args:
            scores (Dict[int, float]): The score for each player.

        Raises:
            MethodNotImplementedError: If the method is not implemented.

        Returns:
            Iterable[Player]: The list of player(s) who won the game.
        """
        raise MethodNotImplementedError()
