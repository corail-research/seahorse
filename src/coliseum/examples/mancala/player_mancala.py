import random

from coliseum.examples.mancala.game_state_mancala import GameStateMancala
from coliseum.game.action import Action
from coliseum.player.player import Player


class PlayerMancala(Player):
    """
    Attributes:
        id_player (int): id of the player
        name (str): name of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    def __init__(self, name: str = "bob") -> None:
        super().__init__(name)


    def solve(self, current_state : GameStateMancala, **kwargs) -> Action:
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
