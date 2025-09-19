import copy
import json
import sys
import time
from abc import abstractmethod
from collections.abc import Container, Iterable
from functools import partialmethod
from itertools import cycle
from typing import Optional

from loguru import logger

from seahorse.game.custom_stat import CustomStat
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster, EventSlave
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import (
    ActionNotPermittedError,
    MethodNotImplementedError,
    PlayerDuplicateError,
    SeahorseTimeoutError,
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
        time_limit: float = 1e9,
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

        self.id2player: dict[int, Player] = {}
        for player in self.get_game_state().get_players() :
            self.id2player[player.get_id()]=player.get_name()

        self.log_level = log_level
        self.players_iterator = cycle(players_iterator) if isinstance(players_iterator, list) else players_iterator
        next(self.players_iterator)
        self.emitter = EventMaster.get_instance(initial_game_state.__class__,port=port,hostname=hostname)
        logger.remove()

        if "VERDICT" not in logger._core.levels:
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

    async def __emit_play_payload__(self) -> None:
        """
        Prepare the game state JSON and add remaining time.
        Emit these infos in a payload through the master's emmiter socket.
        """
        play_payload = self.current_game_state.to_json()
        play_payload["remaining_time"] = self.remaining_time.copy()
        await self.emitter.sio.emit(
            "play",
            json.dumps(play_payload, default=lambda x: x.to_json()),
        )

    async def play_game(self) -> list[Player]:
        """
        Play the game.

        Returns:
            Iterable[Player]: The winner(s) of the game.
        """
        await self.__emit_play_payload__()

        for player in self.players:
            logger.info(f"Player : {player.get_name()} - {player.get_id()}")

        while not self.current_game_state.is_done():
            curent_player_id = self.get_game_state().get_next_player().get_id()
            logger.info(f"Player now playing : {self.get_game_state().get_next_player().get_name()} "
                        f"- {curent_player_id}")
            try:
                self.current_game_state = await self.step()
            except Exception as e:
                if isinstance(e,SeahorseTimeoutError):
                    logger.error(f"Time credit expired for player {self.current_game_state.get_next_player()}: "
                                 f"{self.remaining_time[curent_player_id]}")
                elif isinstance(e,ActionNotPermittedError) :
                    logger.error(f"Action not permitted for player {self.current_game_state.get_next_player()}")
                else:
                    logger.error(f"Player {self.current_game_state.get_next_player()} threw the following exception.")
                    logger.error(str(e))

                temp_score = copy.copy(self.current_game_state.get_scores())
                temp_score[curent_player_id] = -1e9

                for other_player in [player.get_id() for player in self.current_game_state.get_players() if
                                     player.get_id()!=curent_player_id]:
                    temp_score[other_player] = 1e9

                for key in temp_score.keys():
                    logger.info(f"{self.id2player[key]}:{temp_score[key]}")

                for player in self.get_winner(looser_ids={curent_player_id}) :
                    logger.info(f"Winner - {player.get_name()}")

                #TODO: This is counter productive as Seahorse is meant to be independant from the Abyss framework.
                # We should define an abstract method for designers which will fill the infos according to their needs.
                await self.emitter.sio.emit("done",json.dumps({
                    "players": [{"id":player.get_id(), "name":player.get_name()}
                                for player in self.current_game_state.get_players()],
                    "scores": self.get_scores(),
                    "custom_stats": self.get_custom_stats(),
                    "winners_id": [player.get_id() for player in self.get_winner()],
                    "status": "cancelled",
                }))

                logger.verdict(f"{self.current_game_state.get_next_player().get_name()} has been disqualified")

                return self.winner

            logger.info(f"Current game state: \n{self.current_game_state.get_rep()}")

            # Prepare the game state JSON and add remaining time info
            await self.__emit_play_payload__()

        scores = self.get_scores()
        for key in scores.keys():
                logger.info(f"{self.id2player[key]}:{(scores[key])}")

        for player in self.get_winner() :
            logger.info(f"Winner - {player.get_name()}")

        #TODO: Same as todo at line 170.
        await self.emitter.sio.emit("done",json.dumps({
            "players": [{"id":player.get_id(), "name":player.get_name()}
                        for player in self.current_game_state.get_players()],
            "scores": self.get_scores(),
            "custom_stats": self.get_custom_stats(),
            "winners_id": [player.get_id() for player in self.get_winner()],
            "status": "done",
        }))
        logger.verdict(f"{','.join(w.get_name() for w in self.get_winner())} has won the game")
        return self.winner

    async def play_dummy_game(self, k: int=1):
        """
        Play a dummy game for at most k steps and identify if a player is valid.
        Currently, it can only identify invalid one player but will accept more during the play.

        Args:
            k (int): Number of maximum steps for the dummy game.
        """
        await self.__emit_play_payload__()

        for player in self.players:
            logger.info(f"Player : {player.get_name()} - {player.get_id()}")

        i = 0
        while not self.current_game_state.is_done() and i<k:
            curent_player_id = self.get_game_state().get_next_player().get_id()
            logger.info(f"Player now playing : {self.get_game_state().get_next_player().get_name()} "
                        f"- {curent_player_id}")
            try:
                self.current_game_state = await self.step()
            except Exception as e:
                if isinstance(e,SeahorseTimeoutError):
                    logger.error(f"Time credit expired for player {self.current_game_state.get_next_player()}: "
                                 f"{self.remaining_time[curent_player_id]}")
                elif isinstance(e,ActionNotPermittedError) :
                    logger.error(f"Action not permitted for player {self.current_game_state.get_next_player()}")
                else:
                    logger.error(f"Player {self.current_game_state.get_next_player()} threw the following exception.")
                    logger.error(str(e))

                #TODO: make this able to identify multiple invalid agents
                await self.emitter.sio.emit("done",json.dumps({
                    "players": [{"id":player.get_id(), "name":player.get_name()}
                                for player in self.current_game_state.get_players()],
                    "invalid_id": curent_player_id,
                    "status": "invalid",
                }))

                logger.verdict(f"Agent {self.id2player[curent_player_id].get_name()} is invalid")

            logger.info(f"Current game state: \n{self.current_game_state.get_rep()}")

            await self.__emit_play_payload__()

            i += 1


        await self.emitter.sio.emit("done",json.dumps({
            "players": [{"id":player.get_id(), "name":player.get_name()}
                        for player in self.current_game_state.get_players()],
            "status": "valid",
        }))
        logger.verdict(f"Validate agent(s): {[a.get_name() for a in self.players]}")

        return self.winner

    def record_game(self, listeners:Optional[list[EventSlave]]=None) -> None:
        """
        Starts a game and broadcasts its successive states.
        """
        self.emitter.start(self.play_game, self.players+(listeners if listeners else []))

    def record_dummy_game(self, listeners:Optional[list[EventSlave]]=None) -> None:
        """
        Starts a dummy game and broadcasts its successive states.
        """
        self.emitter.start(self.play_dummy_game, self.players+(listeners if listeners else []))

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

    def get_winner(self, looser_ids: Container[int] | None = None) -> list[Player]:
        """
        Arguments:
            looser_ids (Container[int], optional): The IDs of the players who lost the game.
            If provided, the winners will be all players except these ones.
        Returns:
            Player: The winner(s) of the game.

        """
        if not hasattr(self, "winner"):
            if looser_ids is not None:
                self.winner = [player for player in self.current_game_state.get_players()
                               if player.get_id() not in looser_ids]
            else:
                self.winner = self.compute_winner()

        return self.winner

    def get_scores(self) -> dict[int, float]:
        """
        Returns:
            Dict: The scores of the current state.
        """
        return self.current_game_state.get_scores()

    def get_custom_stats(self) -> list[CustomStat]:
        """
        Returns:
            list[CustomState]: The custom statistics of the game.
        """
        if not hasattr(self, "custom_stats"):
            self.custom_stats = self.compute_custom_stats()
        return self.custom_stats

    def compute_custom_stats(self) -> list[CustomStat]:
        """
        Computes custom statistics for the game.
        It should be overridden by subclasses to provide specific statistics.
        It should use self.get_game_state() to access the current game state.
        If should use the format :
        [
            {"name": "stat_name_1", "value": value_1, "agent_id": player_id_1},
            {"name": "stat_name_2", "value": value_2, "agent_id": player_id_2},
            ...
        ]
        Returns:
            list[CustomStat]: A list of dictionaries containing custom statistics.
        """
        return []

    @abstractmethod
    def compute_winner(self) -> list[Player]:
        """
        Computes the winner(s) of the game based on the current game state.

        Raises:
            MethodNotImplementedError: If the method is not implemented.

        Returns:
            Iterable[Player]: The list of player(s) who won the game.
        """
        raise MethodNotImplementedError()
