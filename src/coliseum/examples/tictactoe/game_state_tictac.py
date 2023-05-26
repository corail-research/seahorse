from typing import Dict, List
from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.game.game_state import GameState
from coliseum.player.player import Player
from math import sqrt


class GameStateTictac(GameState):
    """
    Attributes:
        score (list[float]): scores of the state for each players
        next_player (Player): next player to play
        players (list[Player]): list of players
        rep (Representation): representation of the game
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardTictac) -> None:
        super().__init__(scores, next_player, players, rep)
        self.num_pieces = 9

    def get_num_pieces(self):
        """
        Returns:
            num_pieces: number of pieces implied in the game
        """
        return self.num_pieces

    def is_done(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: -
        """
        if len(self.rep.get_env().keys()) == self.num_pieces or self.has_won():
            return True
        return False

    def has_won(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: finish or not
        """
        dim = self.get_num_pieces()
        env = self.rep.get_env()
        table = []
        for k in range(dim):
            table.append(
                [p.get_owner_id() for p in [env.get((i, k), None) for i in range(int(sqrt(dim)))] if p is not None]
            )
            table.append(
                [p.get_owner_id() for p in [env.get((k, i), None) for i in range(int(sqrt(dim)))] if p is not None]
            )
        table.append(
            [p.get_owner_id() for p in [env.get((i, i), None) for i in range(int(sqrt(dim)))] if p is not None]
        )
        table.append(
            [
                p.get_owner_id()
                for p in [env.get((i, int(sqrt(dim)) - i - 1), None) for i in range(int(sqrt(dim)))]
                if p is not None
            ]
        )
        for line in table:
            if len(set(line)) == 1 and len(line) == int(sqrt(dim)):
                return True
        return False

    def __str__(self) -> str:
        print(self.get_rep())
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"
