import copy
import json
from math import sqrt
from typing import Generator, Optional

from board_tictac import BoardTictac
from player_tictac import PlayerTictac

from seahorse.game.stateful_action import StatefulAction
from seahorse.game.stateless_action import StatelessAction
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
        active_player (Player): The player currently taking their turn.
        players (List[Player]): The list of players.
        rep (BoardTictac): The representation of the game.
    """

    def __init__(self, scores: dict, active_player: Player, players: list[Player], rep: BoardTictac, *args, **kwargs) -> None:
        """
        Initializes a new instance of the GameStateTictac class.

        Args:
            scores (Dict): The scores of the state for each player.
            active_player (Player): The player currently taking their turn.
            players (List[Player]): The list of players.
            rep (BoardTictac): The representation of the game.
        """
        super().__init__(scores, active_player, players, rep)
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

    def generate_possible_stateful_actions(self) -> Generator[StatefulAction, None, None]:
        """
        Generates possible actions.

        Returns:
            Generator[StatefulAction]: The possible actions.
        """
        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        active_player = self.get_active_player()
        for i in range(d[0]):
            for j in range(d[1]):
                if not current_rep.get_env().get((i, j)):
                    copy_b = copy.copy(b)
                    copy_b[(i, j)] = Piece(piece_type=active_player.get_piece_type(), owner=active_player)
                    new_board = BoardTictac(copy_b, d)
                    yield StatefulAction(
                        self,
                        GameStateTictac(
                            self.compute_scores(new_board),
                            self.compute_next_player(),
                            self.players,
                            new_board,
                        ),
                    )

    def generate_possible_stateless_actions(self) -> Generator[StatelessAction, None, None]:
        """
        Generates possible actions.

        Returns:
            Generator[StatelessAction]: The possible actions.
        """
        current_rep = self.get_rep()
        d = current_rep.get_dimensions()
        active_player = self.get_active_player()
        for i in range(d[0]):
            for j in range(d[1]):
                if not current_rep.get_env().get((i, j)):
                    yield StatelessAction(
                        data={"position": (i,j), "piece_type": active_player.get_piece_type()},
                    )

    def apply_action(self, action: StatelessAction) -> GameState:
        """
        Applies an action to the game state.

        Args:
            action (StatelessAction): The action to apply.
        Returns:
            GameState: The new game state.
        """
        (i,j) = action.data["position"]
        piece_type = action.data["piece_type"]
        current_rep = self.get_rep()
        b = current_rep.get_env()
        d = current_rep.get_dimensions()
        active_player = self.get_active_player()
        copy_b = copy.copy(b)
        copy_b[(i, j)] = Piece(piece_type=piece_type, owner=active_player)
        new_board = BoardTictac(copy_b, d)
        return GameStateTictac(
            self.compute_scores(new_board),
            self.compute_next_player(),
            self.players,
            new_board,
        )
        
    def compute_scores(self, representation: BoardTictac) -> dict[int, float]:
        scores = {player.get_id(): 0.0 for player in self.players}
        bound = 2.0
        dim = representation.get_dimensions()[0]
        env = representation.get_env()

        for player in self.players:
            player_id = player.get_id()
            rows, cols, diag1, diag2 = [0]*dim, [0]*dim, 0, 0

            for i in range(dim):
                for j in range(dim):
                    if env.get((i, j), None) and env[(i, j)].get_owner_id() == player_id:
                        rows[i] += 1
                        cols[j] += 1
                        if i == j:
                            diag1 += 1
                        if i + j == dim - 1:
                            diag2 += 1

            if any(count > bound for count in rows + cols) or diag1 > bound or diag2 > bound:
                scores[player_id] = 1.0
                scores[next(iter(set(self.players) - {player})).get_id()] = -1.0

        return scores

    def has_won(self) -> bool:
        """
        Checks if a player has won the game.

        Returns:
            bool: True if a player has won, False otherwise.
        """
        return any(score > 0.0 for score in self.scores.values())

    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"

    def to_json(self) -> dict:
        data = { i:j for i,j in self.__dict__.items() if i!="_possible_stateless_actions" and i!="_possible_stateful_actions"}
        return data

    @classmethod
    def from_json(_,data:str,*,active_player:Optional[PlayerTictac]=None) -> Serializable:
        d = json.loads(data)
        scores = {int(k):v for k,v in d["scores"].items()}
        players = [PlayerTictac.from_json(json.dumps(x)) for x in d["players"]]
        rep = BoardTictac.from_json(json.dumps(d["rep"]))

        if active_player is None:
            active_player = players[0]

        return GameStateTictac(scores=scores, active_player=active_player,
                            players=players, rep=rep)