import copy
from math import ceil
from typing import Dict, List, Set
from coliseum.examples.abalone.board_abalone import BoardAbalone

from coliseum.game.action import Action
from coliseum.game.game_layout.board import Piece
from coliseum.game.game_state import GameState
from coliseum.player.player import Player


class GameStateAbalone(GameState):
    """
    Attributes:
        score (list[float]): scores of the state for each players
        next_player (Player): next player to play
        players (list[Player]): list of players
        rep (Representation): representation of the game
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardAbalone) -> None:
        super().__init__(scores, next_player, players, rep)
        self.max_score = -6
        
    def is_done(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: -
        """
        if self.max_score in self.get_scores().values() :
            return True
        else :
            return False

    def detect_conflict(self,i,j,n_i,n_j) -> List[Piece]:
        result = []
        current_rep = self.get_rep()
        b = current_rep.get_env()
        tmp_n_i = n_i
        tmp_n_j = n_j
        my_count = 1
        other_count = 0
        switch = False
        result.append((i,j))
        while b.get((i+tmp_n_i,j+tmp_n_j),False) :
            p = b[(i+tmp_n_i,j+tmp_n_j)]
            if p.get_owner_id() == self.next_player.get_id() and switch == False:
                my_count += 1
                if my_count > 3 :
                    return None
            elif p.get_owner_id() == self.next_player.get_id() and switch == True :
                return None
            else :
                other_count += 1
                switch = True
            if other_count >= my_count :
                return None
            result.append((i+tmp_n_i,j+tmp_n_j))
            tmp_n_i += n_i 
            tmp_n_j += n_j
        return result
    
    def in_hexa(self,index) :
        d = self.get_rep().get_dimensions()
        for i in range(4) :
            for j in range(4-i-1,-1,-1) :
                if index == (i,j) :
                    return False
            for j in range(5+i,9,1) :
                if index == (i,j) :
                    return False
        compteur = 0       
        for i in range(16,12,-1) :
            for j in range(4-1-compteur,-1,-1) :
                if index == (i,j) :
                    return False
            for j in range(5+compteur,9,1) :
                if index == (i,j) :
                    return False
            compteur += 1
            
        return True

    def get_player_id(self,pid) :
        for player in self.players :
            if player.get_id() == pid :
                return player

    def generator(self):
        """
        Function to generate possible actions

        Args:
            current_rep (BoardTictac): current game state representation

        Returns:
            Set[Action]: list of the possible future representation
        """

        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        for i,j in list(b.keys()) :
                p = b.get((i, j), None)
                if p.get_owner_id() == self.next_player.get_id() :
                    list_index = [(-1,-1),(1,-1),(-1,1),(1,1),(2,0),(-2,0)]
                    for n_i, n_j in list_index :
                            to_move_pieces = self.detect_conflict(i,j,n_i,n_j)
                            if to_move_pieces is not None :
                                #print(to_move_pieces)
                                copy_b = copy.copy(b)
                                id_add = None
                                pop_piece = None
                                for k in range(len(to_move_pieces)) :
                                    n_index = to_move_pieces[k]
                                    if n_index[0]+n_i >= 0 and n_index[0]+n_i < d[0] and n_index[1]+n_j >= 0 and n_index[1]+n_j < d[1] and self.in_hexa((n_index[0]+n_i,n_index[1]+n_j)):
                                        copy_b[(n_index[0]+n_i,n_index[1]+n_j,1)] = Piece(piece_type=copy_b[(n_index[0],n_index[1])].get_type(),owner=self.get_player_id(copy_b[(n_index[0],n_index[1])].get_owner_id()))
                                        copy_b.pop((n_index[0],n_index[1]))
                                    else :
                                        id_add = copy_b[(n_index[0],n_index[1])].get_owner_id()
                                        pop_piece = (n_index[0],n_index[1])
                                        copy_b.pop((n_index[0],n_index[1]))
                                for k in range(len(to_move_pieces)) :
                                    n_index = to_move_pieces[k]
                                    if pop_piece != (n_index[0],n_index[1]) :
                                        copy_b[(n_index[0]+n_i,n_index[1]+n_j)] = copy.copy(copy_b[(n_index[0]+n_i,n_index[1]+n_j,1)])
                                        copy_b.pop((n_index[0]+n_i,n_index[1]+n_j,1))
                                #print("dict", len(copy_b))
                                yield BoardAbalone(env=copy_b, dim=d), id_add

    def generate_possible_actions(self) -> List[Action]:

        poss_actions = [
            Action(
                self,
                GameStateAbalone(
                    self.compute_scores(representation=valid_next_rep,id_add=id_add),
                    self.compute_next_player(),
                    self.players,
                    valid_next_rep,
                ),
            )
            for valid_next_rep, id_add in self.generator()
        ]
        #print(len(poss_actions))
        return poss_actions

    def compute_scores(self, representation: BoardAbalone, id_add: int) -> dict[int, float]:
        """
        Function to compute the score of each player in a list

        Args:
            representation (BoardTictac): current representation of the game state

        Returns:
            dict[int,float]: return a dictionnary with id_player: score
        """
        scores = copy.copy(self.scores)
        if id_add is not None :
            scores[id_add] -= 1
                
        # scores = {}
        # for player in self.players:
        #     scores[player.get_id()] = 0
        # b = representation.get_env()
        # for i,j in list(b.keys()) :
        #         p = b.get((i, j), None)
        #         if p is not None:
        #             scores[p.get_owner_id()] += 1

        # TODO print(scores)
        return scores

    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"
