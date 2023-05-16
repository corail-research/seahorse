from coliseum.player.player import Player
from coliseum.game.representation import Representation
from coliseum.utils.custom_exceptions import MethodNotImplementedError

class GameState:
    """
    Attributes:
        score (list[float]): scores of the state for each players
        to_play (Player): next player to play
        players (list[Player]): list of players
        rep (Representation): representation of the game
    """

    def __init__(self,
                 score: list[float],
                 to_play: Player,
                 players: list[Player],
                 rep: Representation
                 ) -> None:
        self.score = score
        self.to_play = to_play
        self.players = players
        self.rep = rep

    def get_next_player(self):
        """
        Returns:
            Player: to_play
        """
        if not self.is_done():
            return self.to_play

    def is_done(self):
        raise MethodNotImplementedError()

    def get_score(self):
        """
        Returns:
            int: score
        """
        return self.score

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

    def update_score(self):
        raise MethodNotImplementedError()

    def update_rep(self):
        raise MethodNotImplementedError()
