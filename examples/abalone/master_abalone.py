from typing import Dict, Iterable, List

from seahorse.game.game_state import GameState
from seahorse.game.master import GameMaster
from seahorse.player.player import Player


class MasterAbalone(GameMaster):
    """
    Master to play the game Abalone

    Attributes:
        name (str): Name of the game
        initial_game_state (GameState): Initial state of the game
        current_game_state (GameState): Current state of the game
        players_iterator (Iterable): An iterable for the players_iterator, ordered according to the playing order.
            If a list is provided, a cyclic iterator is automatically built
        log_file (str): Name of the log file
    """

    def __init__(self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str, port: int = 8080, hostname: str = "localhost", n_listeners: int = 4) -> None:
        super().__init__(name, initial_game_state, players_iterator, log_file, port, hostname, n_listeners)
    def compute_winner(self, scores: Dict[int, float]) -> List[Player]:
        """
        Computes the winners of the game based on the scores.

        Args:
            scores (Dict[int, float]): Score for each player

        Returns:
            Iterable[Player]: List of the players who won the game
        """
        max_val = max(scores.values())
        players_id = list(filter(lambda key: scores[key] == max_val, scores))
        itera = list(filter(lambda x: x.get_id() in players_id, self.players))
        return itera