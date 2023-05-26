from coliseum.game.representation import Representation
from coliseum.player.player import Player


class Action:
    past_rep: Representation
    new_rep: Representation

    def __init__(self) -> None:
        pass

    def get_past_rep(self):
        pass

    def get_new_rep(self):
        pass

    def update_new_rep(self):
        pass

    def check_action(self, player: Player):
        pass
