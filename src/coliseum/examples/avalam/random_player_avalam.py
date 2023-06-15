import random

from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.player.player import Player


class RandomPlayerAvalam(Player):
    """
    Attributes:
        id_player (int): id of the player
        name (str): name of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        super().__init__(name)
        self.piece_type = piece_type

    def get_piece_type(self):
        """
        Returns:
            piece_type: string to represent the type of the piece
        """
        return self.piece_type

    def solve(self, current_state: GameState, **kwargs) -> Action:
        """
        Function to implement the logic of the player (here random selection of a feasible solution)

        Args:
            current_rep (BoardTictac): current representation of the game state
            scores (dict[int, float]): _description_

        Returns:
            BoardTictac: future representation
        """
        possible_actions = current_state.generate_possible_actions()

        if kwargs:
            pass
        return random.choice(list(possible_actions))

    def __str__(self) -> str:
        return super().__str__()
