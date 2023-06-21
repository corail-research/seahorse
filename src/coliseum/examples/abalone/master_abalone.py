from typing import Dict, Iterable

from coliseum.game.game_state import GameState
from coliseum.game.master import GameMaster
from coliseum.player.player import Player


class MasterAbalone(GameMaster):
    """
    Master to play the game Tic Tac Toe

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
        super().__init__(name, initial_game_state, players_iterator, log_file)

    def compute_winner(self, scores: Dict[int, float]) -> Iterable[Player]:
        """Computes the winners of the game based on the scores

        Args:
            scores (Dict[int, float]): score for each player

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Iterable[Player]: list of the player who won the game
        """
        max_val = max(scores.values())
        players_id = list(filter(lambda key: scores[key] == max_val, scores))
        itera = filter(lambda x: x.get_id() in players_id, self.players)
        return itera
