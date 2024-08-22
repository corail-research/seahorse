import copy
import json
import sys
import time
from abc import abstractmethod
from collections.abc import Iterable
from itertools import cycle
from typing import Optional

from loguru import logger

from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster, EventSlave
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import (
    ActionNotPermittedError,
    MethodNotImplementedError,
    PlayerDuplicateError,
    SeahorseTimeoutError,
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
        log_level (str): The name of the log file.
    """

    def __init__(
        self,
        name: str,
        initial_game_state: GameState,
        players_iterator: Iterable[Player],
        log_level: str = "INFO",
        port: int =8080,
        hostname: str ="localhost",
        time_limit: int = 1e9,
    ) -> None:
        """
        Initializes a new instance of the GameMaster class.

        Args:
            name (str): The name of the game.
            initial_game_state (GameState): The initial state of the game.
            players_iterator (Iterable[Player]): An iterable for the players, ordered according
                to the playing order.
            log_level (str): The name of the log file.
        """
        self.timetol = 1e-1
        self.name = name
        self.current_game_state = initial_game_state
        self.players = initial_game_state.players
        self.remaining_time = {player.get_id(): time_limit for player in self.players}

        player_names = [x.name for x in self.players]
        if len(set(player_names))<len(self.players):
            logger.error("Multiple players have the same name this is not allowed.")
            logger.error("Please rename your players such that there is no duplicate in the following list: ")
            logger.error(f"{player_names}")
            raise PlayerDuplicateError()


        self.log_level = log_level
        self.players_iterator = cycle(players_iterator) if isinstance(players_iterator, list) else players_iterator
        next(self.players_iterator)
        self.emitter = EventMaster.get_instance(initial_game_state.__class__,port=port,hostname=hostname)
        logger.remove()

        from functools import partialmethod

        logger.level("VERDICT", no=33, icon="x", color="<blue>")
        logger.__class__.verdict = partialmethod(logger.__class__.log, "VERDICT")

        logger.add(sys.stderr, level=log_level)

    async def step(self) -> GameState:
        """
        Calls the next player move.

        Returns:
            GamseState : The new game_state.
        """
        next_player = self.current_game_state.get_next_player()

        possible_actions = self.current_game_state.get_possible_heavy_actions()

        start = time.time()

        logger.info(f"time : {self.remaining_time[next_player.get_id()]}")
        if isinstance(next_player,EventSlave):
            action = await next_player.play(self.current_game_state, 
                                            remaining_time=self.remaining_time[next_player.get_id()])
        else:
            action = next_player.play(self.current_game_state, 
                                      remaining_time=self.remaining_time[next_player.get_id()])
        tstp = time.time()
        self.remaining_time[next_player.get_id()] -= (tstp-start)
        if self.remaining_time[next_player.get_id()] < 0:
            raise SeahorseTimeoutError()

        action = action.get_heavy_action(self.current_game_state)
        if action not in possible_actions:
            raise ActionNotPermittedError()

        return action.get_next_game_state()

    async def play_game(self) -> list[Player]:
        """
        Play the game.

        Returns:
            Iterable[Player]: The winner(s) of the game.
        """
        await self.emitter.sio.emit(
            "play",
            json.dumps(self.current_game_state.to_json(),default=lambda x:x.to_json()),
        )
        id2player={}
        for player in self.get_game_state().get_players() :
            id2player[player.get_id()]=player.get_name()
            logger.info(f"Player : {player.get_name()} - {player.get_id()}")
        while not self.current_game_state.is_done():
            try:
                logger.info(f"Player now playing : {self.get_game_state().get_next_player().get_name()} - {self.get_game_state().get_next_player().get_id()}")
                self.current_game_state = await self.step()
            except (ActionNotPermittedError,SeahorseTimeoutError,StopAndStartError) as e:
                if isinstance(e,SeahorseTimeoutError):
                    logger.error(f"Time credit expired for player {self.current_game_state.get_next_player()}")
                elif isinstance(e,ActionNotPermittedError) :
                    logger.error(f"Action not permitted for player {self.current_game_state.get_next_player()}")
                temp_score = copy.copy(self.current_game_state.get_scores())
                id_player_error = self.current_game_state.get_next_player().get_id()
                other_player = next(iter([player.get_id() for player in self.current_game_state.get_players() if 
                                          player.get_id()!=id_player_error]))
                temp_score[id_player_error] = -1e9
                temp_score[other_player] = 1e9
                self.winner = self.compute_winner(temp_score)

                for key in temp_score.keys():
                    logger.info(f"{id2player[key]}:{temp_score[key]}")

                for player in self.get_winner() :
                    logger.info(f"Winner - {player.get_name()}")

                await self.emitter.sio.emit("done",json.dumps(self.get_scores()))

                logger.verdict(f"{self.current_game_state.get_next_player().get_name()} has been disqualified")

                return self.winner

            logger.info(f"Current game state: \n{self.current_game_state.get_rep()}")

            await self.emitter.sio.emit(
                "play",
                json.dumps(self.current_game_state.to_json(),default=lambda x:x.to_json()),
            )

        self.winner = self.compute_winner(self.current_game_state.get_scores())
        scores = self.get_scores()
        for key in scores.keys() :
                logger.info(f"{id2player[key]}:{(scores[key])}")

        for player in self.get_winner() :
            logger.info(f"Winner - {player.get_name()}")

        await self.emitter.sio.emit("done",json.dumps(self.get_scores()))
        logger.verdict(f"{','.join(w.get_name() for w in self.get_winner())} has won the game")
        return self.winner

    def record_game(self, listeners:Optional[list[EventSlave]]=None) -> None:
        """
        Starts a game and broadcasts its successive states.
        """
        self.emitter.start(self.play_game, self.players+(listeners if listeners else []))

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
        return self.log_level

    def get_winner(self) -> list[Player]:
        """
        Returns:
            Player: The winner(s) of the game.
        """
        return self.winner

    def get_scores(self) -> dict[int, float]:
        """
        Returns:
            Dict: The scores of the current state.
        """
        return self.current_game_state.get_scores()

    @abstractmethod
    def compute_winner(self, scores: dict[int, float]) -> list[Player]:
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
