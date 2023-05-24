from typing import Dict, List
from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.game.game_state import GameState
from coliseum.player.player import Player


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

    def is_done(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: -
        """
        if len(self.rep.get_env().keys()) == self.num_pieces or self.winning():
            return True
        return False

    def winning(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: finish or not
        """
        dim = self.rep.get_dimensions()

        won = False

        if self.rep.get_env() == {}:
            return False

        for i in range(dim[0]): #check lines
            won = True
            prev = self.rep.get_env().get((i, 0), -1)
            for j in range(dim[1]):
                current = self.rep.get_env().get((i, j), -1)
                if prev == -1 or current == -1:
                    won = False
                    break
                elif current.get_type() != prev.get_type():
                    won = False
            if won:
                return True

        for i in range(dim[1]): #check columns
            won = True
            prev = self.rep.get_env().get((0, i), -1)
            for j in range(dim[0]):
                current = self.rep.get_env().get((j, i), -1)
                if prev == -1 or current == -1:
                    won = False
                    break
                elif current.get_type() != prev.get_type():
                    won = False
            if won:
                return True

        if dim[0] == dim[1]:
            won = True
            prev = self.rep.get_env().get((0, 0), -1)
            for i in range(dim[0]): #check left diag
                current = self.rep.get_env().get((i, i), -1)
                if prev == -1 or current == -1:
                    won = False
                    break
                elif current.get_type() != prev.get_type():
                    won = False
            if won:
                return True

            won = True
            prev = self.rep.get_env().get((dim[0]-1, dim[0]-1), -1)
            for i in range(dim[0]): #check right diag
                current = self.rep.get_env().get((dim[0]-1-i, dim[0]-1-i), -1)
                if prev == -1 or current == -1:
                    won = False
                    break
                elif current.get_type() != prev.get_type():
                    won = False
            if won:
                return True

        return False

    def __str__(self) -> str:
        print(self.get_rep())
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"
