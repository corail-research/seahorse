import copy
import json
from math import sqrt
from typing import Dict, List, Set

from loguru import logger

from board_tictac import BoardTictac
from player_tictac import PlayerTictac
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.game.representation import Representation
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class GameStateTictac(GameState):
    """
    A class representing the game state for Tic-Tac-Toe.

    Attributes:
        score (List[float]): The scores of the state for each player.
        next_player (Player): The next player to play.
        players (List[Player]): The list of players.
        rep (BoardTictac): The representation of the game.
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardTictac, *_, **__) -> None:
        """
        Initializes a new instance of the GameStateTictac class.

        Args:
            scores (Dict): The scores of the state for each player.
            next_player (Player): The next player to play.
            players (List[Player]): The list of players.
            rep (BoardTictac): The representation of the game.
        """
        super().__init__(scores, next_player, players, rep)
        self.num_pieces = self.get_rep().get_dimensions()[0] * self.get_rep().get_dimensions()[1]

    def get_num_pieces(self) -> int:
        """
        Returns the number of pieces implied in the game.

        Returns:
            num_pieces (int): The number of pieces implied in the game.
        """
        return self.num_pieces

    def is_done(self) -> bool:
        """
        Checks if the game is finished.

        Returns:
            bool: True if the game is finished, False otherwise.
        """
        if len(self.rep.get_env().keys()) == self.num_pieces or self.has_won():
            return True
        return False

    def generate_possible_actions(self) -> Set[Action]:
        """
        Generates possible actions.

        Returns:
            Set[Action]: A set of possible future representations.
        """
        list_rep = []
        current_rep = self.get_rep()
        next_player = self.get_next_player()
        for i in range(current_rep.get_dimensions()[0]):
            for j in range(current_rep.get_dimensions()[1]):
                if not current_rep.get_env().get((i, j)):
                    copy_rep = copy.deepcopy(current_rep)
                    copy_rep.get_env()[(i, j)] = Piece(piece_type=next_player.get_piece_type(), owner=next_player)
                    list_rep.append(copy.deepcopy(copy_rep))
        poss_actions = {
            Action(
                self,
                GameStateTictac(
                    self.compute_scores(valid_next_rep),
                    self.compute_next_player(),
                    self.players,
                    valid_next_rep,
                ),
            )
            for valid_next_rep in list_rep
        }
        return poss_actions

    def compute_scores(self, representation: Representation) -> Dict[int, float]:
        """
        Computes the score of each player in a list.

        Args:
            representation (BoardTictac): The current representation of the game state.

        Returns:
            Dict[int, float]: A dictionary with player ID as keys and scores as values.
        """
        scores = {}
        bound = 2.0
        for player in self.players:
            _, pieces = representation.get_pieces_player(player)
            if len(pieces) < representation.get_dimensions()[0]:
                scores[player.get_id()] = 0.0
            else:
                success = False
                env = representation.get_env()
                dim = representation.get_dimensions()[0]
                for i in range(dim):
                    counter = 0.0
                    for j in range(dim):
                        if env.get((i, j), None) and env.get((i, j), None).get_owner_id() == player.get_id():
                            counter += 1.0
                    if counter > bound:
                        scores[player.get_id()] = 1.0
                        success = True
                if success:
                    continue
                for i in range(dim):
                    counter = 0.0
                    for j in range(dim):
                        if env.get((j, i), None) and env.get((j, i), None).get_owner_id() == player.get_id():
                            counter += 1.0
                    if counter > bound:
                        scores[player.get_id()] = 1.0
                        success = True
                if success:
                    continue
                counter = 0.0
                for i in range(dim):
                    if env.get((i, i), None) and env.get((i, i), None).get_owner_id() == player.get_id():
                        counter += 1.0
                if counter > bound:
                    scores[player.get_id()] = 1.0
                    success = True
                if success:
                    continue
                counter = 0.0
                for i in range(dim):
                    if (
                        env.get((i, dim - 1 - i), None)
                        and env.get((i, dim - 1 - i), None).get_owner_id() == player.get_id()
                    ):
                        counter += 1.0
                if counter > bound:
                    scores[player.get_id()] = 1.0
                    success = True
                if success:
                    continue
                else:
                    scores[player.get_id()] = 0.0
        return scores
    
    def convert_light_action_to_action(self,data:Dict) -> Action:
        position = int(data["position"])
        logger.debug(f"Converting light action {data}")
        i = position//3
        j = position%3
        logger.debug(f"{i}{j}")
        for action in self.get_possible_actions():
            if action.get_next_game_state().get_rep().get_env().get((i,j),None) is not None:
                return action
        return None

    def has_won(self) -> bool:
        """
        Checks if a player has won the game.

        Returns:
            bool: True if a player has won, False otherwise.
        """
        dim = self.get_num_pieces()
        env = self.rep.get_env()
        table = []
        for k in range(dim):
            table.append(
                [p.get_owner_id() for p in [env.get((i, k), None) for i in range(int(sqrt(dim)))] if p is not None]
            )
            table.append(
                [p.get_owner_id() for p in [env.get((k, i), None) for i in range(int(sqrt(dim)))] if p is not None]
            )
        table.append(
            [p.get_owner_id() for p in [env.get((i, i), None) for i in range(int(sqrt(dim)))] if p is not None]
        )
        table.append(
            [
                p.get_owner_id()
                for p in [env.get((i, int(sqrt(dim)) - i - 1), None) for i in range(int(sqrt(dim)))]
                if p is not None
            ]
        )
        for line in table:
            if len(set(line)) == 1 and len(line) == int(sqrt(dim)):
                return True
        return False

    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"

    def to_json(self) -> dict:
        return { i:j for i,j in self.__dict__.items() if i!="_possible_actions"}

    @classmethod
    def from_json(cls,data:str,*,next_player:PlayerTictac=None) -> Serializable:
        d = json.loads(data)
        return cls(**{**d,"scores":{int(k):v for k,v in d["scores"].items()},"players":[PlayerTictac.from_json(json.dumps(x)) if not isinstance(x,str) else next_player for x in d["players"]],"next_player":next_player,"rep":BoardTictac.from_json(json.dumps(d["rep"]))})
