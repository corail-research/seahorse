import copy
import json
import sys
import time
from abc import abstractmethod
from collections.abc import Iterable
from itertools import cycle
from typing import List, Optional

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
        hostname: str ="localhost"
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
        self.recorded_plays = []
        self.name = name
        self.current_game_state = initial_game_state
        self.players = initial_game_state.players
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
        possible_actions = self.current_game_state.get_possible_actions()

        start = time.time()
        next_player.start_timer()
        logger.info(f"time : {next_player.get_remaining_time()}")

        if isinstance(next_player,EventSlave):
            action = await next_player.play(self.current_game_state)
        else:
            action = next_player.play(self.current_game_state)

        tstp = time.time()
        if abs((tstp-start)-(tstp-next_player.get_last_timestamp()))>self.timetol:
            next_player.stop_timer()
            raise StopAndStartError()

        next_player.stop_timer()

        if action not in possible_actions:
            raise ActionNotPermittedError()

        action.current_game_state._possible_actions=None
        action.current_game_state=None
        action.next_game_state._possible_actions=None
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
        self.recorded_plays.append(self.current_game_state.__class__.from_json(json.dumps(self.current_game_state.to_json(),default=lambda x:x.to_json())))
        id2player={}
        verdict_scores=[-1e9,-1e9]
        for player in self.get_game_state().get_players() :
            id2player[player.get_id()]=player.get_name()
            logger.info(f"Player : {player.get_name()} - {player.get_id()}")
        while not self.current_game_state.is_done():
            try:
                logger.info(f"Player now playing : {self.get_game_state().get_next_player().get_name()} - {self.get_game_state().get_next_player().get_id()}")
                self.current_game_state = await self.step()
                self.recorded_plays.append(self.current_game_state.__class__.from_json(json.dumps(self.current_game_state.to_json(),default=lambda x:x.to_json())))
            except (ActionNotPermittedError,SeahorseTimeoutError,StopAndStartError) as e:
                if isinstance(e,SeahorseTimeoutError):
                    logger.error(f"Time credit expired for player {self.current_game_state.get_next_player()}")
                elif isinstance(e,ActionNotPermittedError) :
                    logger.error(f"Action not permitted for player {self.current_game_state.get_next_player()}")
                else:
                    logger.error(f"Player {self.current_game_state.get_next_player()} might have tried tampering with the timer.\n The timedelta difference exceeded the allowed tolerancy in GameMaster.timetol ")

                temp_score = copy.copy(self.current_game_state.get_scores())
                id_player_error = self.current_game_state.get_next_player().get_id()
                temp_score.pop(id_player_error)
                self.winner = self.compute_winner(temp_score)
                self.current_game_state.get_scores()[id_player_error] = -3
                other_player = next(iter([player.get_id() for player in self.current_game_state.get_players() if player.get_id()!=id_player_error]))
                self.current_game_state.get_scores()[other_player] = 0
                scores = self.get_scores()
                for key in scores.keys():
                    verdict_scores[int(id2player[key].split("_")[-1])-1]=-scores[key]
                    logger.info(f"{id2player[key]}:{scores[key]}")
                for player in self.get_winner() :
                    logger.info(f"Winner - {player.get_name()}")

                await self.emitter.sio.emit("done",json.dumps(self.get_scores()))
                logger.verdict(f"{verdict_scores[::-1]}")
                with open(self.players[0].name+"_"+self.players[-1].name+"_"+str(time.time())+".json","w+") as f:
                    f.write(json.dumps(self.recorded_plays),default=lambda x:x.to_json())
                return self.winner

            logger.info(f"Current game state: \n{self.current_game_state.get_rep()}")

            await self.emitter.sio.emit(
                "play",
                json.dumps(self.current_game_state.to_json(),default=lambda x:x.to_json()),
            )

        self.winner = self.compute_winner(self.current_game_state.get_scores())
        scores = self.get_scores()
        for key in scores.keys() :
                verdict_scores[int(id2player[key].split("_")[-1])-1]=-scores[key]
                logger.info(f"{id2player[key]}:{(scores[key])}")
        for player in self.get_winner() :
            logger.info(f"Winner - {player.get_name()}")

        await self.emitter.sio.emit("done",json.dumps(self.get_scores()))
        logger.verdict(f"{verdict_scores[::-1]}")
        with open(self.players[0].name+"_"+self.players[-1].name+"_"+str(time.time())+".json","w+") as f:
            f.write(json.dumps(self.recorded_plays,default=lambda x:x.to_json()))
        return self.winner

    def record_game(self, listeners:Optional[List[EventSlave]]=None) -> None:
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
