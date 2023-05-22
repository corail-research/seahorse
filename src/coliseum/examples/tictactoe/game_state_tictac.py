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

    def is_done(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: -
        """
        if len(self.rep.get_env().keys()) == 9 or self.winning():
            return True
        return False

    def winning(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: finish or not
        """
        for i in range(self.rep.get_dimensions()[0]):
            dict_result = {key: 0 for key in self.scores.keys()}
            for j in range(self.rep.get_dimensions()[1]):
                if self.rep.get_env().get((i, j)):
                    dict_result[self.rep.get_env().get((i, j)).get_owner_id()] += 1
            if 3 in dict_result.values():
                return True

        for i in range(self.rep.get_dimensions()[1]):
            dict_result = {key: 0 for key in self.scores.keys()}
            for j in range(self.rep.get_dimensions()[0]):
                if self.rep.get_env().get((i, j)):
                    dict_result[self.rep.get_env().get((i, j)).get_owner_id()] += 1
            if 3 in dict_result.values():
                return True

        dict_result = {key: 0 for key in self.scores.keys()}
        for i in range(self.rep.get_dimensions()[0]):
            if self.rep.get_env().get((i, i)):
                dict_result[self.rep.get_env().get((i, i)).get_owner_id()] += 1
        if 3 in dict_result.values():
            return True

        dict_result = {key: 0 for key in self.scores.keys()}
        for i in range(self.rep.get_dimensions()[0]):
            if self.rep.get_env().get((i, self.rep.get_dimensions()[0] - i)):
                dict_result[self.rep.get_env().get((i, self.rep.get_dimensions()[0] - i)).get_owner_id()] += 1
        if 3 in dict_result.values():
            return True

        return False
