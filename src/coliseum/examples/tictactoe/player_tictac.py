import copy
import random
from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.game.action import Action
from coliseum.game.game_layout.board import Piece
from coliseum.player.player import Player


class PlayerTictac(Player):
    """
    Attributes:
        id_player (int): id of the player
        name (str): name of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    def __init__(self, name: str = "bob") -> None:
        super().__init__(name)

    def get_possible_actions(self, current_rep: BoardTictac) -> list[BoardTictac]:
        """
        Function to generate all the possible actions

        Args:
            current_rep (BoardTictac): current game state representation

        Returns:
            list[BoardTictac]: list of the possible future representation
        """
        list_rep = []
        for i in range(current_rep.get_dimensions()[0]):
            for j in range(current_rep.get_dimensions()[1]):
                if not current_rep.get_env().get((i, j)):
                    copy_rep = copy.deepcopy(current_rep)
                    copy_rep.get_env()[(i, j)] = Piece(piece_type="tic", owner=self)
                    list_rep.append(copy.deepcopy(copy_rep))
        self.possible_actions = list_rep
        return list_rep

    def check_action(self, action: Action) -> bool:
        """
        Function to know if an action is feasible

        Args:
            action (Action): -

        Returns:
            bool: -
        """
        if action.get_new_rep() in self.possible_actions:
            return True
        return False

    def solve(self, current_rep: BoardTictac, **kwargs) -> BoardTictac:
        """
        Function to implement the logic of the player (here random selection of a feasible solution)

        Args:
            current_rep (BoardTictac): current representation of the game state
            scores (dict[int, float]): _description_

        Returns:
            BoardTictac: future representation
        """
        if kwargs:
            pass
        list_possible_rep = self.get_possible_actions(current_rep)
        return random.choice(list_possible_rep)
