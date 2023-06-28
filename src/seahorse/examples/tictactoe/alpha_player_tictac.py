import math
import time
from itertools import cycle

from seahorse.examples.tictactoe.player_tictac import PlayerTictac
from seahorse.game.action import Action
from seahorse.game.game_state import GameState

infinity = math.inf

class MyPlayer(PlayerTictac):
    """
    A class representing an Alpha Player for the Tic-Tac-Toe game.
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initializes a new instance of the AlphaPlayerTictac class.

        Args:
            piece_type (str): The type of game piece assigned to the player.
            name (str, optional): The name of the player. Defaults to "bob".
        """
        super().__init__(piece_type, name)

    def cutoff_depth(self, d: int, cutoff: int) -> bool:
        """
        Checks if the depth has reached the cutoff depth.

        Args:
            d (int): The current depth.
            cutoff (int): The cutoff depth.

        Returns:
            bool: True if the depth has reached the cutoff depth, False otherwise.
        """
        return d > cutoff

    def heuristic(self, current_state: GameState) -> float:
        """
        Calculates the heuristic value for the given game state.

        Args:
            current_state (GameState): The current game state.

        Returns:
            float: The heuristic value.
        """
        players_list = current_state.get_players()
        curr_pos_in_list = players_list.index(self)
        if current_state.get_scores()[self.get_id()] == 1:
            return 1
        elif current_state.get_scores()[next(cycle(players_list[curr_pos_in_list+1:]+players_list[:curr_pos_in_list])).get_id()] == 1:
            return -1
        return 0

    def max_value(self, current_state: GameState, alpha: int, beta: int, depth: int, cutoff: int) -> tuple[float, Action]:
        """
        Performs the max-value step of the alpha-beta algorithm.

        Args:
            current_state (GameState): The current game state.
            alpha (int): The alpha value.
            beta (int): The beta value.
            depth (int): The current depth.
            cutoff (int): The cutoff depth.

        Returns:
            tuple[float, Action]: The value and the corresponding action.
        """
        if self.cutoff_depth(depth, cutoff) or current_state.is_done():
            return self.heuristic(current_state), None
        v, move = -infinity, None
        for a in current_state.get_possible_actions():
            v2, _ = self.min_value(a.get_new_gs(), alpha, beta, depth+1, cutoff)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(self, current_state: GameState, alpha: int, beta: int, depth: int, cutoff: int) -> tuple[float, Action]:
        """
        Performs the min-value step of the alpha-beta algorithm.

        Args:
            current_state (GameState): The current game state.
            alpha (int): The alpha value.
            beta (int): The beta value.
            depth (int): The current depth.
            cutoff (int): The cutoff depth.

        Returns:
            tuple[float, Action]: The value and the corresponding action.
        """
        if self.cutoff_depth(depth, cutoff) or current_state.is_done():
            return self.heuristic(current_state), None
        v, move = +infinity, None
        for a in current_state.get_possible_actions():
            v2, _ = self.max_value(a.get_new_gs(), alpha, beta, depth+1, cutoff)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    def solve(self, current_state: GameState, **_) -> Action:
        """
        Solves the game using the alpha-beta algorithm.

        Args:
            current_state (GameState): The current game state.
            **_: Additional keyword arguments.

        Returns:
            Action: The selected action.
        """
        time.sleep(0.5)
        depth = 0
        cutoff = 2500
        v, move = self.max_value(current_state, -infinity, +infinity, depth, cutoff)

        return move
