from typing import Dict, Iterable

from coliseum.game.game_state import GameState
from coliseum.game.master import GameMaster
from coliseum.player.player import Player


class MasterAvalam(GameMaster):
    """
    Master to play the game Avalam.

    Attributes:
        name (str): Name of the game.
        initial_game_state (GameState): Initial state of the game.
        current_game_state (GameState): Current state of the game.
        players_iterator (Iterable): An iterable for the players_iterator, ordered according to the playing order. 
                                     If a list is provided, a cyclic iterator is automatically built.
        log_file (str): Name of the log file.
    """

    def __init__(
        self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str
    ) -> None:
        """
        Initialize the MasterAvalam instance.

        Args:
            name (str): Name of the game.
            initial_game_state (GameState): Initial state of the game.
            players_iterator (Iterable[Player]): An iterable for the players_iterator, ordered according to the playing order. 
                                                 If a list is provided, a cyclic iterator is automatically built.
            log_file (str): Name of the log file.
        """
        super().__init__(name, initial_game_state, players_iterator, log_file)

    def compute_winner(self, scores: Dict[int, float]) -> Iterable[Player]:
        """
        Computes the winners of the game based on the scores.

        Args:
            scores (Dict[int, float]): Score for each player.

        Raises:
            MethodNotImplementedError: Raised if the method is not implemented.

        Returns:
            Iterable[Player]: List of the player(s) who won the game.
        """
        max_val = max(scores.values())
        players_id = list(filter(lambda key: scores[key] == max_val, scores))
        winners = filter(lambda x: x.get_id() in players_id, self.players)
        return winners
