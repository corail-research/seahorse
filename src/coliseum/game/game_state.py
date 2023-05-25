from abc import abstractmethod
from typing import Dict, List
from coliseum.player.player import Player
from coliseum.game.representation import Representation
from coliseum.utils.custom_exceptions import MethodNotImplementedError


class GameState:
    """
    Attributes:
        score (list[float]): scores of the state for each players
        next_player (Player): next player to play
        players (list[Player]): list of players
        rep (Representation): representation of the game
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: Representation) -> None:
        self.scores = scores
        self.next_player = next_player
        self.players = players
        self.rep = rep

    def get_player_score(self, player: Player) -> float:
        """
        Gets a player's score

        Args:
            player (Player): -

        Returns:
            float: the score
        """
        return self.scores[player.get_id()]

    def get_next_player(self):
        """
        Returns:
            Player: next_player
        """
        if not self.is_done():
            return self.next_player

    def get_scores(self):
        """
        Returns:
            int: score
        """
        return self.scores

    def get_players(self):
        """
        Returns:
            list[Player]: players
        """
        return self.players

    def get_rep(self):
        """
        Returns:
            Representation: rep
        """
        return self.rep

    @abstractmethod
    def is_done(self) -> bool:
        """
        Indicates if the current GameState is final.

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            bool: `True` if the state is final `False` else
        """
        raise MethodNotImplementedError()

    def __str__(self) -> str:
        to_print = f"Current scores are {self.get_scores()}.\n"
        to_print += (
            f"Next person to play is player {self.get_next_player().get_id()} ({self.get_next_player().get_name()}).\n"
        )
        return to_print
