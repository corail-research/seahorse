import json
from abc import abstractmethod
from itertools import cycle
from typing import Dict, Iterable

from coliseum.game.game_state import GameState
from coliseum.game.io_stream import EventMaster
from coliseum.player.player import Player
from coliseum.utils.custom_exceptions import ActionNotPermittedError, MethodNotImplementedError


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
        self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str
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
        self.emitter = EventMaster.get_instance(2)

    async def step(self) -> GameState:
        """
        Calls the next player move.

        Returns:
            GamseState : The new game_state.
        """
        next_player = self.current_game_state.get_next_player()
        possible_actions = self.current_game_state.get_possible_actions()

        next_player.start_timer()
        action = await next_player.play(self.current_game_state)
        next_player.stop_timer()

        if action not in possible_actions:
            raise ActionNotPermittedError()

        return action.get_new_gs()

    async def play_game(self) -> Iterable[Player]:
        """
        Play the game.

        Returns:
            Iterable[Player]: The winner(s) of the game.
        """
        await self.emitter.sio.emit(
            "play",
            json.dumps(
                self.current_game_state.__dict__, default=lambda o: o.to_json() if hasattr(o, "to_json") else "bob"
            ),
        )
        while not self.current_game_state.is_done():
            self.current_game_state = await self.step()
            #print(self.current_game_state.get_rep())
            #print(self.current_game_state)
            await self.emitter.sio.emit(
                "play",
                json.dumps(
                    self.current_game_state.__dict__, default=lambda o: o.to_json() if hasattr(o, "to_json") else "bob"
                ),
            )
        self.winner = self.compute_winner(self.current_game_state.get_scores())
        for _w in self.winner:
            pass
        return self.winner

    def record_game(self) -> None:
        """
        Starts a game and broadcasts its successive states.
        """
        self.emitter.start(self.play_game, self.players)

    def update_log(self):
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

    def get_winner(self) -> Player:
        """
        Returns:
            Player: The winner(s) of the game.
        """
        return self.winner

    @abstractmethod
    def compute_winner(self, scores: Dict[int, float]) -> Iterable[Player]:
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
