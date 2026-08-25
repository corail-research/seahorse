import copy
import json
import sys
from abc import abstractmethod
from collections.abc import Container, Iterable
from functools import partialmethod

from loguru import logger

from seahorse.game.custom_stat import CustomStat
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster, EventSlave
from seahorse.player.player import Player
from seahorse.player.proxies import PlayerProxy
from seahorse.utils.custom_exceptions import (
    ActionNotPermittedError,
    MethodNotImplementedError,
    PlayerDuplicateError,
    SeahorseTimeoutError,
)


class GameMaster:
    """
    Base class representing the game master.

    The game master is the central orchestrator managing game flow,
    player interactions, and state transitions.

    The GameMaster is responsible for:
        - Managing game state progression
        - Enforcing game rules and time limits
        - Coordinating player actions
        - Broadcasting game events to listeners
        - Determining game outcomes and winners

    Attributes:
        name (str): Display name of the game.
        current_game_state (GameState): Current state of the game.
        players (list[Player]): List of participating players.
        players_proxy (list[PlayerProxy]):
            List of player proxies for communication.
        remaining_time (dict[int, float]):
            Dictionary mapping player IDs to their remaining time.
        id2player (dict[int, PlayerProxy]):
            Dictionary mapping player IDs to player proxies.
        log_level (str): Logging verbosity level.
        emitter (EventMaster): Event emitter for broadcasting game state.


    """

    def __init__(
        self,
        name: str,
        initial_game_state: GameState,
        players_iterator: Iterable[PlayerProxy],
        log_level: str = "INFO",
        port: int = 8080,
        hostname: str = "localhost",
        time_limit: float = 1e9,
    ) -> None:
        """
        Initializes a new instance of the GameMaster class.

        Args:
            name (str): Display name of the game.
            initial_game_state (GameState): Starting state of the game.
            players_iterator (Iterable[PlayerProxy]):
                Iterable of player proxies in turn order.
            log_level (str): Logging level. Defaults to "INFO".
            port (int):
                WebSocket port for event broadcasting.
                Defaults to 8080.
            hostname (str):
                Hostname for event broadcasting.
                Defaults to "localhost".
            time_limit (float):
                Time limit in seconds for each player.
                Defaults to 1e9.

        Raises:
            PlayerDuplicateError: If multiple players have the same name.
            ValueError: If players_iterator is not a valid iterable.

        Note:
            Each player is automatically assigned
            a time credit equal to `time_limit`.
            [Players][.....player.player.Player] with duplicate names
            are not allowed and will raise an exception.
        """
        self.name = name
        self.current_game_state = initial_game_state
        self.players = initial_game_state.players
        self.players_proxy = list(players_iterator)
        self.remaining_time = {
            player.get_id(): time_limit for player in self.players}

        player_names = [x.name for x in self.players]
        if len(set(player_names)) < len(self.players):
            logger.error(
                "Multiple players have the same name this is not allowed.")
            logger.error(
                "Please rename your players such that "
                "there is no duplicate in the following list: ")
            logger.error(f"{player_names}")
            raise PlayerDuplicateError()

        if not isinstance(players_iterator, Iterable):
            msg = "Player iterator must be a valid iterator object"
            raise ValueError(msg)

        self.id2player: dict[int, PlayerProxy] = {}
        for player in players_iterator:
            self.id2player[player.get_id()] = player

        self.log_level = log_level

        self.emitter = EventMaster.get_instance(
            initial_game_state.__class__, port=port, hostname=hostname)
        logger.remove()

        if "VERDICT" not in logger._core.levels:
            logger.level("VERDICT", no=33, icon="x", color="<blue>")
            logger.__class__.verdict = partialmethod(
                logger.__class__.log, "VERDICT")

        logger.add(sys.stderr, level=log_level)

    async def step(self) -> GameState:
        """
        Executes a single game step by requesting
        and processing the next player's move.

        Returns:
            GameState: New game state after the player turn.

        Raises:
            SeahorseTimeoutError: If the player exceeds their remaining time.
            ActionNotPermittedError: If the chosen action is not valid.

        Note:
            Deducts the computation time from the player's remaining time credit.

        """
        next_player = self.id2player[self.current_game_state.get_active_player(
        ).get_id()]

        logger.info(f"time : {self.remaining_time[next_player.get_id()]}s")

        try:
            action, time_diff = await next_player.play(current_state=self.current_game_state,
                                                       remaining_time=self.remaining_time[next_player.get_id()])
        except TimeoutError as timeout:
            raise SeahorseTimeoutError() from timeout

        self.remaining_time[next_player.get_id()] -= time_diff
        if self.remaining_time[next_player.get_id()] + self.timetol < 0:
            msg = SeahorseTimeoutError().message + \
                str(self.remaining_time[next_player.get_id()])
            raise SeahorseTimeoutError(msg)

        possible_actions = self.current_game_state.get_possible_stateful_actions()

        action = action.get_stateful_action(self.current_game_state)
        if action not in possible_actions:
            raise ActionNotPermittedError()

        return action.get_next_game_state()

    async def _emit_play_payload(self) -> None:
        # Prepares and broadcasts the current game state via WebSocket.

        play_payload = self.current_game_state.to_json()
        play_payload["remaining_time"] = self.remaining_time.copy()
        await self.emitter.sio.emit(
            "play",
            json.dumps(play_payload, default=lambda x: x.to_json()),
        )

    async def play_game(self) -> list[Player]:
        """
        Executes a complete game from start to finish.

        Returns:
            list[Player]: List of winning players.

        Raises:
            Exception: Propagates any unexpected player exceptions.

        Note:
            - Game continues until a terminal state is reached.
            - Disqualifies players who cause exceptions or timeout.
            - Broadcasts game state after each move.
            - Logs detailed game progression and final verdict.

        Example:
            Print all winners after playing the game.

            ``` python
            >>> winners = await game_master.play_game()
            >>> for winner in winners:
            ...     print(f"Winner: {winner.get_name()}")
            ```
        """
        await self._emit_play_payload()

        for player in self.players:
            logger.info(f"Player : {player.get_name()} - {player.get_id()}")

        while not self.current_game_state.is_done():
            current_player = self.get_current_game_state().get_active_player()
            logger.info("Player now playing : "
                        f"{current_player.get_name()}"
                        f" - {current_player.get_id()}")
            try:
                self.current_game_state = await self.step()
            except Exception as e:
                if isinstance(e, SeahorseTimeoutError):
                    exp_time = self.remaining_time[current_player.get_id()]
                    logger.error("Time credit expired for player "
                                 f"{current_player}: "
                                 f"{exp_time}")
                elif isinstance(e, ActionNotPermittedError):
                    logger.error(
                        f"Action not permitted for {current_player}")
                else:
                    logger.error(
                        f"{self.current_game_state.get_active_player()} threw the following exception:")
                    logger.exception(e)

                temp_score = copy.copy(self.current_game_state.get_scores())
                temp_score[current_player.get_id()] = -1e9

                for other_player in [player.get_id()
                                     for player in self.current_game_state.get_players()
                                     if player.get_id() != current_player.get_id()]:
                    temp_score[other_player] = 1e9

                for key in temp_score.keys():
                    logger.info(f"{self.id2player[key]}:{temp_score[key]}")

                for player in self.get_winner(
                        looser_ids={current_player.get_id()}):
                    logger.info(f"Winner - {player.get_name()}")

                # TODO: This is counter productive.
                # Seahorse is meant to be independant from the Abyss framework.
                # We should define an abstract method for designers
                # which will fill the infos according to their needs.
                await self.emitter.sio.emit("done", json.dumps({
                    "players": [{"id": player.get_id(),
                                 "name": player.get_name()}
                                for player in self.current_game_state.get_players()],
                    "scores": self.get_scores(),
                    "custom_stats": self.get_custom_stats(),
                    "winners_id": [player.get_id()
                                   for player in self.get_winner()],
                    "status": "cancelled",
                }))

                logger.verdict(
                    f"{current_player.get_name()} has been disqualified")

                return self.winner

            logger.info(
                f"Current game state: \n{self.current_game_state.get_rep()}")

            # Prepare the game state JSON and add remaining time info
            await self._emit_play_payload()

        scores = self.get_scores()
        for key in scores.keys():
            logger.info(f"{self.id2player[key]}:{(scores[key])}")

        for player in self.get_winner():
            logger.info(f"Winner - {player.get_name()}")

        # TODO: Same as todo at line 170.
        await self.emitter.sio.emit("done", json.dumps({
            "players": [{"id": player.get_id(), "name": player.get_name()}
                        for player in self.current_game_state.get_players()],
            "scores": self.get_scores(),
            "custom_stats": self.get_custom_stats(),
            "winners_id": [player.get_id() for player in self.get_winner()],
            "status": "done",
        }))

        logger.verdict(
            f"{','.join(w.get_name() for w in self.get_winner())}"
            " has won the game")

        return self.get_winner()

    # TODO: This and play_game could be refactored
    # to have less redunbdante lines
    async def play_dummy_game(self, k: int = 1):
        """
        Runs a limited game to validate player implementations.

        Executes at most k steps to check if players can produce valid moves
        without causing exceptions or timing out.

        Args:
            k (int): Maximum number of steps to execute. Defaults to 1.

        Note:
            - Stops early if game reaches terminal state.
            - Does not compute final winners.
            - Broadcasts preliminary agent validation and invalidation.
        """
        await self._emit_play_payload()

        for player in self.players:
            logger.info(f"Player : {player.get_name()} - {player.get_id()}")

        i = 0
        while not self.current_game_state.is_done() and i < k:

            current_player = self.get_current_game_state().get_active_player()
            logger.info("Player now playing : "
                        f"{current_player.get_name()}"
                        f" - {current_player.get_id()}")
            try:
                self.current_game_state = await self.step()
            except Exception as e:
                if isinstance(e, SeahorseTimeoutError):
                    exp_time = self.remaining_time[current_player.get_id()]
                    logger.error("Time credit expired for player "
                                 f"{current_player}: "
                                 f"{exp_time}")
                elif isinstance(e, ActionNotPermittedError):
                    logger.error("Action not permitted for player"
                                 f"{current_player}")
                else:
                    logger.error(
                        f"{self.current_game_state.get_active_player()} threw the following exception:")
                    logger.exception(e)

                # TODO: make this able to identify multiple invalid agents
                await self.emitter.sio.emit("done", json.dumps({
                    "players": [{"id": player.get_id(),
                                 "name": player.get_name()}
                                for player
                                in self.current_game_state.get_players()],
                    "invalid_id": current_player.get_id(),
                    "status": "invalid",
                }))

                logger.verdict(
                    f"Agent {current_player.get_name()} is invalid")

            logger.info(
                f"Current game state: \n{self.current_game_state.get_rep()}")

            await self._emit_play_payload()

            i += 1

        await self.emitter.sio.emit("done", json.dumps({
            "players": [{"id": player.get_id(),
                         "name": player.get_name()}
                        for player in self.current_game_state.get_players()],
            "status": "valid",
        }))

        logger.verdict(
            f"Validate agent(s): {[a.get_name() for a in self.players]}")

    def record_game(self, listeners: list[EventSlave] | None = None) -> None:
        """
        Starts a complete game and broadcasts it to listeners.

        Args:
            listeners (list[EventSlave] | None):
                Optional list of EventSlave instances to receive broadcasts.
                If None, only the player proxies will receive updates.

        Note:
            This is a synchronous wrapper
            around the asynchronous play_game method.
            It starts the event emitter and manages the game lifecycle.
        """
        self.emitter.start(self.play_game,
                           self.players_proxy+(listeners if listeners else []),
                           self._close)

    def record_dummy_game(self, listeners: list[EventSlave] | None = None) -> None:
        """
        Starts a validation game and broadcasts it to listeners.

        Args:
            listeners (list[EventSlave] | None):
                Optional list of EventSlave instances to receive broadcasts.
                If None, only the player proxies will receive updates.

        Note:
            This is a synchronous wrapper around the play_dummy_game method.
            Used for agent validation in a broadcast context.
        """
        self.emitter.start(self.play_dummy_game,
                           self.players_proxy+(listeners if listeners else []),
                           self._close)

    async def _close(self):
        """
        Closes all player proxy connections.

        Returns:
            None: This method doesn't return a value.

        Note:
            Should be called to clean up resources after game completion.
            Automatically called by record_game and record_dummy_game.
        """
        for player_proxy in self.players_proxy:
            await player_proxy.close()

    def get_name(self) -> str:
        """
        Retrieves the name of the game.

        Returns:
            str: Game name as specified during initialization.
        """
        return self.name

    def get_current_game_state(self) -> GameState:
        """
        Retrieves the current game state.

        Returns:
            GameState: Current GameState object.
        """
        return self.current_game_state

    def get_winner(self, looser_ids: Container[int] | None = None) -> list[Player]:
        """
        Determines the winning players, optionally excluding specified losers.

        Args:
            looser_ids (Container[int] | None):
                Container of player IDs to exclude from winners.
                If provided, winners are all players not in this container.

        Returns:
            List of Player objects who won the game.

        Note:
            Results are cached after first computation.
            Subsequent calls with different looser_ids will
            return the cached result from the first call.
        """
        if not hasattr(self, "winner"):
            if looser_ids is not None:
                self.winner = [player for player
                               in self.current_game_state.get_players()
                               if player.get_id() not in looser_ids]
            else:
                self.winner = self.compute_winner()

        return self.winner

    def get_scores(self) -> dict[int, float]:
        """
        Retrieves current scores for all players.

        Returns:
            Dictionary mapping player IDs to their current scores.

        Example:
            Print all players scores.

            ``` python
            >>> scores = game_master.get_scores()
            >>> for player_id, score in scores.items():
            ...     print(f"Player {player_id}: {score}")
            ```
        """
        return self.current_game_state.get_scores()

    def get_custom_stats(self) -> list[CustomStat]:
        """
        Retrieves custom statistics for the game.

        Returns:
            List of CustomStat objects containing game-specific statistics.

        Note:
            Statistics are computed once and cached.
            Uses [compute_custom_stats][..compute_custom_stats]
            for the initial computation.
        """
        if not hasattr(self, "custom_stats"):
            self.custom_stats = self.compute_custom_stats()
        return self.custom_stats

    def compute_custom_stats(self) -> list[CustomStat]:
        """
        Computes game-specific custom statistics.

        Returns:
            List of CustomStat objects.

        Note:
            This method should be overridden by game designers
            to provide meaningful statistics.
            The base implementation returns an empty list.
        """
        return []

    @abstractmethod
    def compute_winner(self) -> list[Player]:
        """
        Abstract method to determine winners based on game rules.

        Returns:
            List of Player objects who won the game.

        Note:
            Must be implemented by game designers to define winning conditions.
            Should analyze the current game state to determine winners.
            This method is called internally by [get_winner][..get_winner].
        """
        raise MethodNotImplementedError()
