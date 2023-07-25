from __future__ import annotations

import copy
import json
from typing import TYPE_CHECKING

from seahorse.examples.abalone.board_abalone import BoardAbalone
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable
if TYPE_CHECKING:
    from seahorse.examples.abalone.game_state_abalone import GameStateAbalone


class PlayerAbalone(Player):
    """
    A player class implementing the Alpha-Beta algorithm for the Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", **kwargs) -> None:
        """
        Initializes a new instance of the AlphaPlayerAbalone class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str, optional): The name of the player. Defaults to "bob".
        """
        super().__init__(name,**kwargs)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        """
        Gets the type of the player's game piece.

        Returns:
            str: The type of the player's game piece.
        """
        return self.piece_type

    def convert_light_action_to_action(self,src:tuple[int, int], dst:tuple[int, int], current_game_state:GameStateAbalone) ->  Action :
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

    def toJson(self) -> str:
        return json.dumps(self.__dict__,default=lambda x:x.toJson() if isinstance(x,Serializable) else None)

    @classmethod
    def fromJson(cls, data) -> Serializable:
        return PlayerAbalone(**json.loads(data))
