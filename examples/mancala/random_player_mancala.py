import random
from argparse import Action

from game_state_mancala import GameStateMancala
from player_mancala import PlayerMancala


class MyPlayer(PlayerMancala):
    """
    A class representing a Mancala player.

    Attributes:
        name (str): The name of the player.

    Args:
        name (str): The name of the player.
    """

    def __init__(self, name: str = "bob") -> None:
        """
        Initializes a new instance of the PlayerMancala class.

        Args:
            name (str): The name of the player.
        """
        super().__init__(name)


    def compute_action(self, current_state: GameStateMancala, **kwargs) -> Action:
        """
        Solves the game by implementing the logic of the player (random selection of a feasible solution).

        Args:
            current_state (GameStateMancala): The current game state.
            **kwargs: Additional keyword arguments.

        Returns:
            Action: The selected action.
        """
        possible_actions = current_state.generate_possible_actions()
        if kwargs:
            pass
        return random.choice(list(possible_actions))
