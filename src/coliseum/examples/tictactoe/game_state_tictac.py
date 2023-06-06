import copy
from math import sqrt
from typing import Dict, List, Set

from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.game.action import Action
from coliseum.game.game_layout.board import Piece
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

    def generate_possible_actions(self) -> Set[Action]:
        """
        Function to generate possible actions

        Args:
            current_rep (BoardTictac): current game state representation

        Returns:
            Set[Action]: list of the possible future representation
        """

        list_rep = []
        current_rep = self.get_rep()
        next_player = self.get_next_player()
        for i in range(current_rep.get_dimensions()[0]):
            for j in range(current_rep.get_dimensions()[1]):
                if not current_rep.get_env().get((i, j)):
                    copy_rep = copy.deepcopy(current_rep)
                    copy_rep.get_env()[(i, j)] = Piece(
                        piece_type=next_player.get_piece_type(), owner=next_player)
                    list_rep.append(copy.deepcopy(copy_rep))
        poss_actions = {Action(self, valid_next_rep)
                           for valid_next_rep in list_rep}

        return poss_actions

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
                [p.get_owner_id() for p in [env.get((i, k), None)
                                            for i in range(int(sqrt(dim)))] if p is not None]
            )
            table.append(
                [p.get_owner_id() for p in [env.get((k, i), None)
                                            for i in range(int(sqrt(dim)))] if p is not None]
            )
        table.append(
            [p.get_owner_id() for p in [env.get((i, i), None)
                                        for i in range(int(sqrt(dim)))] if p is not None]
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
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"
