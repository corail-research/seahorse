import math

from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.player.player import Player

infinity = math.inf

class AlphaPlayerAbalone(Player):
    """
    Attributes:
        id_player (int): id of the player
        name (str): name of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        super().__init__(name)
        self.piece_type = piece_type

    def get_piece_type(self):
        """
        Returns:
            piece_type: string to represent the type of the piece
        """
        return self.piece_type

    def cutoff_depth(self, d, cutoff):
        return d > cutoff

    def heuristic(self, current_state : GameState):
        # TODO: review to make beautiful
        players_list = current_state.get_players()
        players_list.index(self)
        return current_state.get_scores()[self.get_id()]

    def max_value(self, current_state : GameState, alpha : int, beta : int, depth : int, cutoff : int):
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

    def min_value(self, current_state : GameState, alpha : int, beta : int, depth : int, cutoff : int):

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

    def solve(self, current_state : GameState, **_) -> Action:
        """
        Function to implement the logic of the player (here alpha beta algorithm)
        """
        depth = 0
        cutoff = 2
        v, move = self.max_value(current_state, -infinity, +infinity, depth, cutoff)
        #print(self.get_id(), v)
        #v, move = self.min_value(current_state, -infinity, +infinity, depth, cutoff)

        return move

    def __str__(self) -> str:
        return super().__str__()
