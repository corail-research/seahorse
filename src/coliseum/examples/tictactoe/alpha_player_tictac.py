import math
import time
from itertools import cycle

from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.examples.tictactoe.player_tictac import PlayerTictac

infinity = math.inf

class AlphaPlayerTictac(PlayerTictac):
    """
    Attributes:
        id_player (int): id of the player
        name (str): name of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        super().__init__(piece_type, name)

    def cutoff_depth(self, d, cutoff):
        return d > cutoff

    def heuristic(self, current_state : GameState):
        # TODO: review to make beautiful
        players_list = current_state.get_players()
        curr_pos_in_list = players_list.index(self)
        if current_state.get_scores()[self.get_id()] == 1:
            return 1
        elif current_state.get_scores()[next(cycle(players_list[curr_pos_in_list+1:]+players_list[:curr_pos_in_list])).get_id()] == 1:
            return -1
        return 0

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
        time.sleep(0.5)
        depth = 0
        cutoff = 2500
        v, move = self.max_value(current_state, -infinity, +infinity, depth, cutoff)
        #print(self.get_id(), v)
        #v, move = self.min_value(current_state, -infinity, +infinity, depth, cutoff)

        return move

    def __str__(self) -> str:
        return super().__str__()
