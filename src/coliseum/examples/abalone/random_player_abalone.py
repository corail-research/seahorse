import random

from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.player.player import Player

class RandomPlayerAbalone(Player):
    """
    Player class for Abalone game that makes random moves.

    Attributes:
        id_player (int): ID of the player
        name (str): Name of the player

    Class Attributes:
        next_id (int): ID to be assigned to the next player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initialize the RandomPlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
        """
        super().__init__(name)
        self.piece_type = piece_type

    def get_piece_type(self):
        """
        Get the type of the player's game piece.

        Returns:
            str: Piece type string representing the type of the piece
        """
        return self.piece_type

    def solve(self, current_state: GameState, **kwargs) -> Action:
        """
        Function to implement the logic of the player (here random selection of a feasible solution).

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: Randomly selected feasible action
        """
        possible_actions = current_state.get_possible_actions()
        random.seed("seahorse")
        if kwargs:
            pass
        return random.choice(list(possible_actions))
