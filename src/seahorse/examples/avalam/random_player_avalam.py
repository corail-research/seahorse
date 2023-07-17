import random

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player


class MyPlayer(Player):
    """
    A player class that makes random moves in the game Avalam.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initialize the RandomPlayerAvalam instance.

        Args:
            piece_type (str): The type of the player's piece.
            name (str, optional): The name of the player. Defaults to "bob".
        """
        super().__init__(name)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        """
        Get the type of the player's piece.

        Returns:
            str: The type of the piece.
        """
        return self.piece_type

    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Implement the logic of the player by randomly selecting a feasible solution.

        Args:
            current_state (GameState): The current game state.
            **kwargs: Additional keyword arguments.

        Returns:
            Action: The chosen action.
        """
        possible_actions = current_state.get_possible_actions()
        random.seed("seahorse")
        if kwargs:
            pass
        return random.choice(list(possible_actions))
