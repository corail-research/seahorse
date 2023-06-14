import math
from math import sqrt
import time

from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.player.player import Player

infinity = math.inf

class AlphaPlayerTictac(Player):
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
        if current_state.get_scores().get(self.id_player) == 1:
            return 1
        elif current_state.get_scores().get(1-self.id_player) == 1:
            return -1
        return 0
        dim = current_state.get_num_pieces()
        env = current_state.rep.get_env()
        table = []
        for k in range(dim):
            table.append(
                [p.get_owner_id() for p in [env.get((i, k), None)
                                            for i in range(int(sqrt(dim)))] if p is not None]
            )
            table.append(
                [p.get_owner_id() for p in [env.get((k, i), None)
                                            for i in range(int(sqrt(dim)))] if p is not None]
            )
        table.append(
            [p.get_owner_id() for p in [env.get((i, i), None)
                                        for i in range(int(sqrt(dim)))] if p is not None]
        )
        table.append(
            [
                p.get_owner_id()
                for p in [env.get((i, int(sqrt(dim)) - i - 1), None) for i in range(int(sqrt(dim)))]
                if p is not None
            ]
        )
        for line in table:
            if len(set(line)) == 1 and len(line) == int(sqrt(dim)) and line[0] == self.get_id():
                return 1
            elif len(set(line)) == 1 and len(line) == int(sqrt(dim)) and line[0] != self.get_id():
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
        print(self.get_id(), v)
        #v, move = self.min_value(current_state, -infinity, +infinity, depth, cutoff)

        return move

    def __str__(self) -> str:
        return super().__str__()
