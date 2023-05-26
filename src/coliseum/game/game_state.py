from coliseum.game.representation import Representation
from coliseum.player.player import Player


class GameState:
    score: list[float]
    to_play: Player
    players: list[Player]
    rep: Representation

    def __init__(self) -> None:
        pass

    def get_next_player(self):
        pass

    def is_done(self):
        pass

    def get_score(self):
        pass

    def get_to_play(self):
        pass

    def get_players(self):
        pass

    def get_rep(self):
        pass

    def update_score(self):
        pass

    def update_rep(self):
        pass
