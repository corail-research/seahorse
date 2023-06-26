import copy
from typing import Dict, List, Set

from coliseum.examples.avalam.board_avalam import BoardAvalam, PieceAvalam
from coliseum.game.action import Action
from coliseum.game.game_state import GameState
from coliseum.player.player import Player

class GameStateAvalam(GameState):
    """
    GameState class for the Avalam game.

    Attributes:
        scores (Dict): Scores of the state for each player
        next_player (Player): Next player to play
        players (List[Player]): List of players
        rep (BoardAvalam): Representation of the game
        max_tower (int): Maximum tower height
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardAvalam) -> None:
        """
        Initialize the GameStateAvalam instance.

        Args:
            scores (Dict): Scores of the state for each player
            next_player (Player): Next player to play
            players (List[Player]): List of players
            rep (BoardAvalam): Representation of the game
        """
        super().__init__(scores, next_player, players, rep)
        self.max_tower = 5

    def is_done(self) -> bool:
        """
        Check if the game is finished.

        Returns:
            bool: True if the game is finished, False otherwise
        """
        b = self.get_rep().get_env()
        for i, j in b.keys():
            p = b[(i,j)]
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

    def generate_possible_actions(self) -> Set[Action]:
        """
        Generate possible actions.

        Returns:
            Set[Action]: Set of possible actions
        """
        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        actions = set()
        compteur = 0
        for i, j in list(b.keys()):
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
                                id_sub = p.get_owner_id()
                                owner = [player for player in self.players if player.get_id() == owner_id][0]
                                copy_rep[(i, j)] = PieceAvalam(
                                    piece_type=piece_type, owner=owner, value=v + v_n
                                )
                                copy_rep.pop((i + n_i, j + n_j))
                                action = Action(
                                    self,
                                    GameStateAvalam(
                                        self.compute_scores(id_sub),
                                        self.compute_next_player(),
                                        self.players,
                                        BoardAvalam(env=copy_rep,dim=d),
                                    ),
                                )
                                compteur += 1
                                actions.add(action)
        return actions

    def compute_scores(self, id_sub) -> Dict[int, float]:
        """
        Compute the score of each player in a dictionary.

        Args:
            id_sub: ID of the player

        Returns:
            Dict[int, float]: Dictionary with player ID as key and score as value
        """
        scores = copy.copy(self.scores)
        scores[id_sub] -= 1
        return scores

    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"
