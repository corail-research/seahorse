import json
from abc import abstractmethod
from itertools import cycle
from typing import Dict, Iterable, List

from coliseum.game.game_state import GameState
from coliseum.game.io_stream import EventMaster
from coliseum.player.player import Player
from coliseum.utils.custom_exceptions import ActionNotPermittedError, MethodNotImplementedError


class GameMaster:
    """
    Attributes:
        name (str): name of the game
        initial_game_state (GameState): initial state of the game
        current_game_state (GameState): initial state of the game
        players_iterator (Iterable): an iterable for the players_iterator, ordered according
                            to the playing order. If a list is provided,
                            a cyclic iterator is automatically built
        log_file (str): name of the log file
    """

    def __init__(
        self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str
    ) -> None:
        self.name = name
        self.current_game_state = initial_game_state
        self.initial_game_state = initial_game_state
        # TODO check if this should be passed in init arguments
        self.players = initial_game_state.players
        self.log_file = log_file
        self.players_iterator = cycle(players_iterator) if isinstance(players_iterator, list) else players_iterator
        # TODO (to review) Pop the first (because already referenced at init)
        next(self.players_iterator)
        self.emitter = EventMaster.get_instance(3)

    @staticmethod
    def get_next_player(player : Player, players_list : List[Player], *_)->Player:
        """
        Function to get the next player

        Args:
            player (Player): current player
            current_rep (Representation): current representation of the game
            next_rep (Representation): next representation of the game

        Returns:
            Player: next player
        """
        curr_id = players_list.index(player)
        return next(cycle(players_list[curr_id+1:]+players_list[:curr_id]))


    async def step(self) -> GameState:
        """
        Calls the next player move
        """
        next_player = self.current_game_state.get_next_player()
        possible_actions = self.current_game_state.generate_possible_actions()

        next_player.start_timer()
        action = await next_player.play(self.current_game_state)
        next_player.stop_timer()

        if action not in possible_actions:
            raise ActionNotPermittedError()

        # TODO check against possible hacking
        #new_scores = self.compute_scores(action.get_new_rep())
        return action.get_new_gs()

    async def play_game(self) -> Iterable[Player]:
        """Play the game

        Returns:
            Player: winner of the game
        """
        #print(self.current_game_state.get_rep())
        await self.emitter.sio.emit("play", json.dumps(self.current_game_state.__dict__,default = lambda o: o.to_json()  if hasattr(o, "to_json") else "bob"))
        while not self.current_game_state.is_done():
            self.current_game_state = await self.step()
            #print(self.current_game_state)
            await self.emitter.sio.emit("play", json.dumps(self.current_game_state.__dict__,default = lambda o: o.to_json()  if hasattr(o, "to_json") else "bob"))
            #TODO - outputting module print(self.current_game_state)
        self.winner = self.compute_winner(self.current_game_state.get_scores())
        for _w in self.winner:
            #TODO - outputting module print("Winner :", w)
            pass
        return self.winner

    def record_game(self) -> None:
        """
            Starts a game and broadcasts its successive states
        """
        self.emitter.start(self.play_game, self.players)

    def update_log(self):
        # TODO: Implement I/O utilities for logging
        raise MethodNotImplementedError()

    def get_name(self):
        """
        Returns:
            str: name
        """
        return self.name

    def get_game_state(self):
        """
        Returns:
            GameState: game_state
        """
        return self.current_game_state

    def get_json_path(self):
        """
        Returns:
            str: log_file
        """
        return self.log_file

    def get_winner(self):
        """
        Returns:
            Player: winner of the game
        """
        return self.winner


    @abstractmethod
    def compute_winner(self, scores: Dict[int, float]) -> Iterable[Player]:
        """Computes the winners of the game based on the scores

        Args:
            scores (Dict[int, float]): score for each player

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Iterable[Player]: list of the player who won the game
        """
        raise MethodNotImplementedError()
