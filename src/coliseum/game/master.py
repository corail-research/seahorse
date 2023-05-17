from abc import abstractmethod
import copy
from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.game.representation import Representation
from coliseum.player.player import Player
from coliseum.utils.custom_exceptions import ActionNotPermittedError, MethodNotImplementedError
from typings import Iterable,List
from itertools import cycle


class Master:
    """
    Attributes:
        name (str): name of the game
        initial_game_state (GameState): initial state of the game
        current_game_state (GameState): initial state of the game
        players (Iterable): an iterable for the players, ordered according
                            to the playing order. If a list is provided,
                            a cyclic iterator is automatically built
        log_file (str): name of the log file
    """

    def __init__(self,
                 name: str,
                 initial_game_state: GameState,
                 players: Iterable[Player],
                 log_file: str
                 ) -> None:
        self.name = name
        self.current_game_state = initial_game_state
        self.initial_game_state = initial_game_state
        self.log_file = log_file
        self.players = cycle(players) if isinstance(players, list) else players

    def step(self) -> GameState:
        """
            Calls the next player move
        """
        next_player = self.current_game_state.get_next_player()
        action =  next_player.play(self.current_game_state)
        if not action.check_action(next_player):
            raise ActionNotPermittedError()
        
        # TODO check against possible hacking
        new_scores = self.compute_scores(action.get_new_rep())

        return GameState(new_scores,next(self.players),self.players,action.get_new_rep())

    def play_game(self) -> Player:
        """_summary_

        Returns:
            Player: winner of the game
        """
        while(not self.current_game_state.is_done()):
            self.current_game_state = self.step()

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
        return self.game_state

    def get_json_path(self):
        """
        Returns:
            str: log_file
        """
        return self.log_file
    
    @abstractmethod
    def compute_scores(self,representation:Representation)->List[float]:
        raise MethodNotImplementedError()
