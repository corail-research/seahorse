import random

from seahorse.examples.avalam.player_avalam import PlayerAvalam
from seahorse.game.action import Action
from seahorse.game.game_state import GameState


class MyPlayer(PlayerAvalam):
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
        super().__init__(piece_type, name)

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
