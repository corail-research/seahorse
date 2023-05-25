from abc import abstractmethod
from typing import Dict, List
from coliseum.game.game_state import GameState
from coliseum.game.representation import Representation
from coliseum.player.player import Player
from coliseum.utils.custom_exceptions import ActionNotPermittedError, MethodNotImplementedError
from typing import Iterable
from itertools import cycle


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

    def step(self) -> GameState:
        """
        Calls the next player move
        """
        next_player = self.current_game_state.get_next_player()
        next_player.start_timer()
        action = next_player.play(self.current_game_state)
        next_player.stop_timer()
        if not next_player.check_action(action):
            raise ActionNotPermittedError()

        # TODO check against possible hacking
        new_scores = self.compute_scores(action.get_new_rep())
        return self.initial_game_state.__class__(
            new_scores, next(self.players_iterator), self.players, action.get_new_rep()
        )

    def play_game(self) -> Iterable[Player]:
        """Play the game

        Returns:
            Player: winner of the game
        """
        while not self.current_game_state.is_done():
            self.current_game_state = self.step()
            print(self.current_game_state)
        self.winner = self.compute_winner(self.current_game_state.get_scores())
        for w in self.winner:
            print("Winner :", w)
        return self.winner

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
    def compute_scores(self, representation: Representation) -> Dict[int, float]:
        """Computes the scores of each player

        Args:
            representation (Representation): _description_

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            List[float]: _description_
        """
        raise MethodNotImplementedError()

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
