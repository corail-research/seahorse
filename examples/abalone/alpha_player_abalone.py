import math
from typing import Tuple

from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState

infinity = math.inf

class MyPlayer(PlayerAbalone):
    """
    A player class implementing the Alpha-Beta algorithm for the Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initializes a new instance of the AlphaPlayerAbalone class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str, optional): The name of the player. Defaults to "bob".
        """
        super().__init__(piece_type, name)

    def cutoff_depth(self, d: int, cutoff: int) -> bool:
        """
        Checks if the given depth exceeds the cutoff.

        Args:
            d (int): The current depth.
            cutoff (int): The cutoff depth.

        Returns:
            bool: True if the cutoff depth is exceeded, False otherwise.
        """
        return d > cutoff

    def heuristic(self, current_state: GameState) -> int:
        """
        Computes the heuristic value for the given game state.

        Args:
            current_state (GameState): The current game state.

        Returns:
            int: The heuristic value.
        """
        id_next_player = self.get_id()
        for player in current_state.get_players():
            if player.get_id() != id_next_player:
                id_player = player.get_id()
        return 2 * current_state.get_scores()[self.get_id()] - current_state.get_scores()[id_player]

    def max_value(self, current_state: GameState, alpha: int, beta: int, depth: int, cutoff: int) -> Tuple[int, Action]:
        """
        Computes the maximum value for the current player in the Alpha-Beta algorithm.

        Args:
            current_state (GameState): The current game state.
            alpha (int): The alpha value.
            beta (int): The beta value.
            depth (int): The current depth.
            cutoff (int): The cutoff depth.

        Returns:
            Tuple[int, Action]: The maximum value and the corresponding action.
        """
        if self.cutoff_depth(depth, cutoff) or current_state.is_done():
            return self.heuristic(current_state), None
        v, move = -infinity, None
        for a in current_state.get_possible_actions():
            v2, _ = self.min_value(a.get_next_game_state(), alpha, beta, depth + 1, cutoff)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(self, current_state: GameState, alpha: int, beta: int, depth: int, cutoff: int) -> Tuple[int, Action]:
        """
        Computes the minimum value for the opponent player in the Alpha-Beta algorithm.

        Args:
            current_state (GameState): The current game state.
            alpha (int): The alpha value.
            beta (int): The beta value.
            depth (int): The current depth.
            cutoff (int): The cutoff depth.

        Returns:
            Tuple[int, Action]: The minimum value and the corresponding action.
        """
        if self.cutoff_depth(depth, cutoff) or current_state.is_done():
            return self.heuristic(current_state), None
        v, move = +infinity, None
        for a in current_state.get_possible_actions():
            v2, _ = self.max_value(a.get_next_game_state(), alpha, beta, depth + 1, cutoff)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    def compute_action(self, current_state: GameState, **_) -> Action:
        """
        Solves the game by implementing the logic of the player using the Alpha-Beta algorithm.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The selected action.
        """
        depth = 0
        cutoff = 2
        v, move = self.max_value(current_state, -infinity, +infinity, depth, cutoff)
        return move
