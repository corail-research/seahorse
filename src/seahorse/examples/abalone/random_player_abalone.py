import random

from seahorse.examples.abalone.player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState


class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initialize the RandomPlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
        """
        super().__init__(piece_type,name)


    def compute_action(self, current_state: GameState, **kwargs) -> Action:
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
