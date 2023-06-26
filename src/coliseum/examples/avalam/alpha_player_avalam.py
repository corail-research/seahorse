import math

from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.player.player import Player

infinity = math.inf

class AlphaPlayerAvalam(Player):
    """
    Player class for Avalam game that uses the alpha-beta algorithm for move selection.

    Attributes:
        id_player (int): ID of the player
        name (str): Name of the player

    Class Attributes:
        next_id (int): ID to be assigned to the next player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initialize the AlphaPlayerAvalam instance.

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

    def cutoff_depth(self, d: int, cutoff: int) -> bool:
        """
        Check if the depth has reached the cutoff value.

        Args:
            d (int): Current depth
            cutoff (int): Cutoff depth

        Returns:
            bool: True if the depth is greater than the cutoff, False otherwise
        """
        return d > cutoff

    def heuristic(self, current_state: GameState) -> float:
        """
        Evaluate the current state using a heuristic function.

        Args:
            current_state (GameState): Current game state representation

        Returns:
            float: Heuristic value of the current state
        """
        players_list = current_state.get_players()
        players_list.index(self)
        return current_state.get_scores()[self.get_id()]

    def max_value(self, current_state: GameState, alpha: int, beta: int, depth: int, cutoff: int) -> tuple[float, Action]:
        """
        Perform the max-value step of the alpha-beta algorithm.

        Args:
            current_state (GameState): Current game state representation
            alpha (int): Alpha value for pruning
            beta (int): Beta value for pruning
            depth (int): Current depth in the search tree
            cutoff (int): Cutoff depth

        Returns:
            tuple[float, Action]: Tuple containing the max-value and the corresponding action
        """
        if self.cutoff_depth(depth, cutoff) or current_state.is_done():
            return self.heuristic(current_state), None
        v, move = -infinity, None
        for a in current_state.get_possible_actions():
            v2, _ = self.min_value(a.get_new_gs(), alpha, beta, depth + 1, cutoff)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(self, current_state: GameState, alpha: int, beta: int, depth: int, cutoff: int) -> tuple[float, Action]:
        """
        Perform the min-value step of the alpha-beta algorithm.

        Args:
            current_state (GameState): Current game state representation
            alpha (int): Alpha value for pruning
            beta (int): Beta value for pruning
            depth (int): Current depth in the search tree
            cutoff (int): Cutoff depth

        Returns:
            tuple[float, Action]: Tuple containing the min-value and the corresponding action
        """
        if self.cutoff_depth(depth, cutoff) or current_state.is_done():
            return self.heuristic(current_state), None
        v, move = +infinity, None
        for a in current_state.get_possible_actions():
            v2, _ = self.max_value(a.get_new_gs(), alpha, beta, depth + 1, cutoff)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    def solve(self, current_state: GameState, **_) -> Action:
        """
        Function to implement the logic of the player (alpha-beta algorithm).

        Args:
            current_state (GameState): Current game state representation
            **_: Additional keyword arguments

        Returns:
            Action: Selected action based on the alpha-beta algorithm
        """
        depth = 0
        cutoff = 2
        v, move = self.max_value(current_state, -infinity, +infinity, depth, cutoff)

        return move
