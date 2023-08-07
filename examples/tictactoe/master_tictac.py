from typing import Dict, Iterable, List

from seahorse.game.game_state import GameState
from seahorse.game.master import GameMaster
from seahorse.player.player import Player


class MasterTictac(GameMaster):
    """
    A game master for playing Tic Tac Toe.

    Attributes:
        name (str): The name of the game.
        initial_game_state (GameState): The initial state of the game.
        current_game_state (GameState): The current state of the game.
        players_iterator (Iterable): An iterable for the players_iterator, ordered according
                                    to the playing order. If a list is provided,
                                    a cyclic iterator is automatically built.
        log_file (str): The name of the log file.
    """

    def __init__(self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str, port: int = 8080, hostname: str = "localhost", n_listeners: int = 4) -> None:
        super().__init__(name, initial_game_state, players_iterator, log_file, port, hostname, n_listeners=n_listeners)

    def compute_winner(self, scores: Dict[int, float]) -> List[Player]:
        """
        Computes the winners of the game based on the scores.

        Args:
            scores (Dict[int, float]): The score for each player.

        Returns:
            Iterable[Player]: A list of the players who won the game.
        """
        max_val = max(scores.values())
        players_id = [key for key in scores if scores[key] == max_val]
        winners = [player for player in self.players if player.get_id() in players_id]
        return winners
