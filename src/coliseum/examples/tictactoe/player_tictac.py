import random
from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.game.representation import Representation
from coliseum.player.player import Player


class PlayerTictac(Player):
    def __init__(self, name: str = "bob") -> None:
        super().__init__(name)

    def get_possible_actions(self, rep: BoardTictac) -> list[BoardTictac]:
        return

    def solve(self, current_rep: BoardTictac, scores: dict[int, float], **kwargs) -> BoardTictac:
        list_possible_rep = self.get_possible_actions(current_rep)
        return random.choice(list_possible_rep)
