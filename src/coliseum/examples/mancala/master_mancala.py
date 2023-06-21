from typing import Dict, Iterable

from coliseum.game.game_state import GameState
from coliseum.game.master import GameMaster
from coliseum.player.player import Player


class MasterMancala(GameMaster):

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
        if scores[self.players[0].get_id()] > scores[self.players[1].get_id()]:
            return [p for p in self.players if p.get_id() == 0]
        elif scores[self.players[0].get_id()] < scores[self.players[1].get_id()]:
            return [p for p in self.players if p.get_id() == 1]
