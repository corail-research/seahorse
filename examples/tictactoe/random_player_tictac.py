import random

from player_tictac import PlayerTictac

from seahorse.game.action import Action
from seahorse.game.game_state import GameState


class MyPlayer(PlayerTictac):
    """
    A player class for Tic Tac Toe that selects moves randomly.
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initializes a new instance of the RandomPlayerTictac class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str): The name of the player.
        """
        super().__init__(piece_type, name)

    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Implements the logic of the player by randomly selecting a feasible move.

        Args:
            current_state (GameState): The current game state.
            **kwargs: Additional keyword arguments.

        Returns:
            Action: The selected action.
        """
        possible_actions = current_state.generate_possible_actions()

        return random.choice(list(possible_actions))
