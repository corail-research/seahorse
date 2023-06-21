import copy
from typing import Dict, List, Set

from coliseum.examples.avalam.board_avalam import BoardAvalam, PieceAvalam
from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.player.player import Player


class GameStateAvalam(GameState):
    """
    Attributes:
        score (list[float]): scores of the state for each players
        next_player (Player): next player to play
        players (list[Player]): list of players
        rep (Representation): representation of the game
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardAvalam) -> None:
        super().__init__(scores, next_player, players, rep)
        self.max_tower = 5

    def is_done(self) -> bool:
        """
        Function to know if the game is finished

        Returns:
            bool: -
        """
        b = self.get_rep().get_env()
        d = self.get_rep().get_dimensions()
        for i in range(d[0]):
            for j in range(d[1]):
                p = b.get((i, j), None)
                if p is not None:
                    v = p.get_value()
                    n_index = [-1, 0, 1]
                    for n_i in n_index:
                        for n_j in n_index:
                            if not (n_i == 0 and n_j == 0):
                                n = b.get((i + n_i, j + n_j), None)
                                if n is not None:
                                    v_n = n.get_value()
                                    if v + v_n <= self.max_tower:
                                        return False
        return True

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
                v = p.get_value()
                n_index = [-1, 0, 1]
                for n_i in n_index:
                    for n_j in n_index:
                        if not (n_i == 0 and n_j == 0):
                            n = b.get((i + n_i, j + n_j), None)
                            if n is not None:
                                v_n = n.get_value()
                                if v + v_n <= self.max_tower:
                                    copy_rep = copy.copy(current_rep.get_env())
                                    piece_type = n.get_type()
                                    owner_id = n.get_owner_id()
                                    #print(owner_id, piece_type, v + v_n)
                                    owner = [player for player in self.players if player.get_id() == owner_id][0]
                                    copy_rep[(i, j)] = PieceAvalam(
                                        piece_type=piece_type, owner=owner, value=v + v_n
                                    )
                                    copy_rep.pop((i + n_i, j + n_j))
                                    #print(1)
                                    #print("Avant :",copy_rep)
                                    yield BoardAvalam(env=copy_rep,dim=d)
                                    #print(2)
                                    #list_next_rep.append(copy.deepcopy(copy_rep))
                                    #current_rep.get_env()[(i, j)] = p
                                    #current_rep.get_env()[(i + n_i, j + n_j)] = n
                                    #print("Après : ", current_rep)

    def generate_possible_actions(self) -> Set[Action]:

        poss_actions = {
            Action(
                self,
                GameStateAvalam(
                    self.compute_scores(valid_next_rep),
                    self.compute_next_player(),
                    self.players,
                    valid_next_rep,
                ),
            )
            for valid_next_rep in self.generator()
        }

        return poss_actions

    def compute_scores(self, representation: BoardAvalam) -> dict[int, float]:
        """
        Function to compute the score of each player in a list

        Args:
            representation (BoardTictac): current representation of the game state

        Returns:
            dict[int,float]: return a dictionnary with id_player: score
        """
        scores = {}
        for player in self.players:
            scores[player.get_id()] = 0
        b = representation.get_env()
        for i,j in list(b.keys()) :
                p = b.get((i, j), None)
                if p is not None:
                    scores[p.get_owner_id()] += 1

        # TODO print(scores)
        return scores

    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"
