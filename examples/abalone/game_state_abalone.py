import copy
import json
from typing import Dict, List, Set, Tuple

from seahorse.examples.abalone.board_abalone import BoardAbalone
from seahorse.examples.abalone.player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class GameStateAbalone(GameState):
    """
    A class representing the state of an Abalone game.

    Attributes:
        score (list[float]): Scores of the state for each player.
        next_player (Player): Next player to play.
        players (list[Player]): List of players.
        rep (Representation): Representation of the game.
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardAbalone, step: int, *args, **kwargs) -> None:
        super().__init__(scores, next_player, players, rep)
        self.max_score = -6
        self.max_step = 50
        self.step = step

    def get_step(self) -> int:
        """
        Return the current step of the game.

        Returns:
            int: The current step of the game.
        """
        return self.step

    def is_done(self) -> bool:
        """
        Check if the game is finished.

        Returns:
            bool: True if the game is finished, False otherwise.
        """
        if self.step == self.max_step or self.max_score in self.scores.values():
            return True
        else:
            return False

    def detect_conflict(self, i: int, j: int, n_i: int, n_j: int) -> List[Tuple[int, int]]:
        """
        Detect conflicts on the board.

        Args:
            i (int): Row index of the starting position.
            j (int): Column index of the starting position.
            n_i (int): Row direction of movement.
            n_j (int): Column direction of movement.

        Returns:
            List[Piece]: List of pieces involved in the conflict.
        """
        result = []
        current_rep = self.get_rep()
        b = current_rep.get_env()
        tmp_n_i = n_i
        tmp_n_j = n_j
        my_count = 1
        other_count = 0
        switch = False
        max_deplacement = 3
        result.append((i, j))
        while b.get((i + tmp_n_i, j + tmp_n_j), False):
            p = b[(i + tmp_n_i, j + tmp_n_j)]
            if p.get_owner_id() == self.next_player.get_id() and switch is False:
                my_count += 1
                if my_count > max_deplacement:
                    return None
            elif p.get_owner_id() == self.next_player.get_id() and switch is True:
                return None
            else:
                other_count += 1
                switch = True
            if other_count >= my_count:
                return None
            result.append((i + tmp_n_i, j + tmp_n_j))
            tmp_n_i += n_i
            tmp_n_j += n_j
        return result

    def in_hexa(self, index) -> bool:
        """
        Check if a given index is within the hexagonal game board.

        Args:
            index: The index to check.

        Returns:
            bool: True if the index is within the hexagonal game board, False otherwise.
        """
        for i in range(4):
            for j in range(4 - i - 1, -1, -1):
                if index == (i, j):
                    return False
            for j in range(5 + i, 9, 1):
                if index == (i, j):
                    return False
        compteur = 0
        for i in range(16, 12, -1):
            for j in range(4 - 1 - compteur, -1, -1):
                if index == (i, j):
                    return False
            for j in range(5 + compteur, 9, 1):
                if index == (i, j):
                    return False
            compteur += 1

        return True

    def get_player_id(self, pid) -> Player:
        """
        Get the player with the given ID.

        Args:
            pid: The ID of the player.

        Returns:
            Player: The player with the given ID.
        """
        for player in self.players:
            if player.get_id() == pid:
                return player

    def generator(self):
        """
        Generate possible actions.

        Returns:
            Set[Action]: List of possible future representations.
        """
        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        for i, j in list(b.keys()):
            p = b.get((i, j), None)
            if p.get_owner_id() == self.next_player.get_id():
                list_index = [(-1, -1), (1, -1), (-1, 1), (1, 1), (2, 0), (-2, 0)]
                for n_i, n_j in list_index:
                    to_move_pieces = self.detect_conflict(i, j, n_i, n_j)
                    if to_move_pieces is not None:
                        copy_b = copy.copy(b)
                        id_add = None
                        pop_piece = None
                        for k in range(len(to_move_pieces)):
                            n_index = to_move_pieces[k]
                            if (
                                n_index[0] + n_i >= 0
                                and n_index[0] + n_i < d[0]
                                and n_index[1] + n_j >= 0
                                and n_index[1] + n_j < d[1]
                                and self.in_hexa((n_index[0] + n_i, n_index[1] + n_j))
                            ):
                                copy_b[(n_index[0] + n_i, n_index[1] + n_j, 1)] = Piece(
                                    piece_type=copy_b[(n_index[0], n_index[1])].get_type(),
                                    owner=self.get_player_id(copy_b[(n_index[0], n_index[1])].get_owner_id()),
                                )
                                copy_b.pop((n_index[0], n_index[1]))
                            else:
                                id_add = copy_b[(n_index[0], n_index[1])].get_owner_id()
                                pop_piece = (n_index[0], n_index[1])
                                copy_b.pop((n_index[0], n_index[1]))
                        for k in range(len(to_move_pieces)):
                            n_index = to_move_pieces[k]
                            if pop_piece != (n_index[0], n_index[1]):
                                copy_b[(n_index[0] + n_i, n_index[1] + n_j)] = copy.copy(
                                    copy_b[(n_index[0] + n_i, n_index[1] + n_j, 1)]
                                )
                                copy_b.pop((n_index[0] + n_i, n_index[1] + n_j, 1))
                        yield BoardAbalone(env=copy_b, dim=d), id_add

    def generate_possible_actions(self) -> Set[Action]:
        """
        Generate possible actions for the current game state.

        Returns:
            List[Action]: List of possible actions.
        """
        poss_actions = {
            Action(
                self,
                GameStateAbalone(
                    self.compute_scores(id_add=id_add),
                    self.compute_next_player(),
                    self.players,
                    valid_next_rep,
                    step=self.step + 1,
                ),
            )
            for valid_next_rep, id_add in self.generator()
        }
        return poss_actions

    def convert_light_action_to_action(self,data) ->  Action :
        src,dst=data['from'],data['to']
        current_game_state = self
        b = current_game_state.get_rep().get_env()
        d = current_game_state.get_rep().get_dimensions()
        n_i, n_j = dst[0]-src[0],dst[1]-src[1]
        to_move_pieces = current_game_state.detect_conflict(src[0],src[1],n_i,n_j)
        if to_move_pieces is not None:
            copy_b = copy.copy(b)
            id_add = None
            pop_piece = None
            for k in range(len(to_move_pieces)):
                n_index = to_move_pieces[k]
                if (
                    n_index[0] + n_i >= 0
                    and n_index[0] + n_i < d[0]
                    and n_index[1] + n_j >= 0
                    and n_index[1] + n_j < d[1]
                    and current_game_state.in_hexa((n_index[0] + n_i, n_index[1] + n_j))
                ):
                    copy_b[(n_index[0] + n_i, n_index[1] + n_j, 1)] = Piece(
                        piece_type=copy_b[(n_index[0], n_index[1])].get_type(),
                        owner=current_game_state.get_player_id(copy_b[(n_index[0], n_index[1])].get_owner_id()),
                    )
                    copy_b.pop((n_index[0], n_index[1]))
                else:
                    id_add = copy_b[(n_index[0], n_index[1])].get_owner_id()
                    pop_piece = (n_index[0], n_index[1])
                    copy_b.pop((n_index[0], n_index[1]))
            for k in range(len(to_move_pieces)):
                n_index = to_move_pieces[k]
                if pop_piece != (n_index[0], n_index[1]):
                    copy_b[(n_index[0] + n_i, n_index[1] + n_j)] = copy.copy(
                        copy_b[(n_index[0] + n_i, n_index[1] + n_j, 1)]
                    )
                    copy_b.pop((n_index[0] + n_i, n_index[1] + n_j, 1))
            return Action(
                    current_game_state,
                    GameStateAbalone(
                        current_game_state.compute_scores(id_add=id_add),
                        current_game_state.compute_next_player(),
                        current_game_state.players,
                        BoardAbalone(env=copy_b, dim=d),
                        step=current_game_state.step + 1,
                        ),
                    )
        return None

    def compute_scores(self, id_add: int) -> Dict[int, float]:
        """
        Compute the score of each player in a list.

        Args:
            id_add (int): The ID of the player to add the score for.

        Returns:
            dict[int, float]: A dictionary with player ID as the key and score as the value.
        """
        scores = copy.copy(self.scores)
        if id_add is not None:
            scores[id_add] -= 1

        # TODO print(scores)
        return scores

    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"

    def to_json(self) -> str:
        return { i:j for i,j in self.__dict__.items() if i!="_possible_actions"}

    @classmethod
    def from_json(cls,data:str,*,next_player:PlayerAbalone=None) -> Serializable:
        d = json.loads(data)
        return cls(**{**d,"scores":{int(k):v for k,v in d["scores"].items()},"players":[PlayerAbalone.from_json(json.dumps(x)) if not isinstance(x,str) else next_player for x in d["players"]],"next_player":next_player,"rep":BoardAbalone.from_json(json.dumps(d["rep"]))})

