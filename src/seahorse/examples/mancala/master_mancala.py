from typing import Dict, Iterable, List

from seahorse.game.game_state import GameState
from seahorse.game.master import GameMaster
from seahorse.player.player import Player


class MasterMancala(GameMaster):
    """
    A class representing the game master for Mancala.

    Attributes:
        name (str): The name of the game master.
        initial_game_state (GameState): The initial game state.
        players_iterator (Iterable[Player]): An iterable of players.
        log_file (str): The log file.
    """

    def __init__(
        self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str
    ) -> None:
        """
        Initializes a new instance of the MasterMancala class.

        Args:
            name (str): The name of the game master.
            initial_game_state (GameState): The initial game state.
            players_iterator (Iterable[Player]): An iterable of players.
            log_file (str): The log file.
        """
        super().__init__(name, initial_game_state, players_iterator, log_file)

    def compute_winner(self, scores: Dict[int, float]) -> List[Player]:
        """
        Computes the winners of the game based on the scores.

        Args:
            scores (Dict[int, float]): The score for each player.

        Raises:
            MethodNotImplementedError: If the method is not implemented.

        Returns:
            Iterable[Player]: A list of the player(s) who won the game.
        """
        if scores[self.players[0].get_id()] > scores[self.players[1].get_id()]:
            return [p for p in self.players if p.get_id() == 0]
        elif scores[self.players[0].get_id()] < scores[self.players[1].get_id()]:
            return [p for p in self.players if p.get_id() == 1]
        return self.players
