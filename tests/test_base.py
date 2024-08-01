import copy
import unittest
from typing import Any

from seahorse.game.game_layout.board import Board, Piece
from seahorse.game.game_state import GameState
from seahorse.game.heavy_action import HeavyAction
from seahorse.game.representation import Representation
from seahorse.player.player import Player


class DummyGameState(GameState):

    def __init__(self, scores: dict[int, Any], next_player: Player, players: list[Player], rep: Representation) -> None:
        super().__init__(scores, next_player, players, rep)

    def generate_possible_actions(self):
        list_rep = []
        current_rep = self.get_rep()
        next_player = self.get_next_player()
        for i in range(current_rep.get_dimensions()[0]):
            for j in range(current_rep.get_dimensions()[1]):
                if not current_rep.get_env().get((i, j)):
                    copy_rep = copy.deepcopy(current_rep)
                    copy_rep.get_env()[(i, j)] = Piece(piece_type="Added", owner=next_player)
                    list_rep.append(copy.deepcopy(copy_rep))
        poss_actions = {
            HeavyAction(
                self,
                DummyGameState(
                    self.get_scores(),
                    self.compute_next_player(),
                    self.players,
                    valid_next_rep,
                ),
            )
            for valid_next_rep in list_rep
        }

        return poss_actions


class TestCase(unittest.TestCase):

    def setUp(self):
        self.board = Board(env={}, dim=[3, 3])

        self.player1 = Player("Thomas")
        self.player2 = Player(identifier=42)

        self.piece1 = Piece("A")
        self.piece2 = Piece("B", self.player2)
        self.piece3 = Piece("C", self.player1)

        self.current_gs = DummyGameState(scores={self.player1.get_id():1, self.player2.get_id():0},
                                          next_player=self.player1, players=[self.player1, self.player2], rep=self.board)

    def test_id(self):
        assert self.player1.get_id() == id(self.player1)
        assert self.player2.get_id() == 42
        assert self.piece1.get_owner_id() == -1
        assert self.piece2.get_owner_id() == self.player2.get_id()

    def test_board(self):
        assert self.board.get_dimensions() == [3,3]
        assert self.board.get_env() == {}
        assert self.board.get_pieces_player(self.player1) == (0, [])
        self.board.env[(0, 1)] = self.piece1
        self.board.env[(2, 1)] = self.piece2
        self.board.env[(2, 2)] = self.piece3
        assert self.board.get_pieces_player(self.player1) == (1, [(2, 2)])
        assert self.board.get_pieces_player(self.player2) == (1, [(2, 1)])

    def test_gamestate(self):
        assert self.current_gs.compute_next_player() == self.player2
        assert self.current_gs.get_player_score(self.player1) == 1
        self.board.env[(0, 1)] = self.piece1
        possible_actions = self.current_gs.generate_possible_actions()
        assert len(possible_actions) == self.current_gs.get_rep().get_dimensions()[0]*self.current_gs.get_rep()\
            .get_dimensions()[1] - 1
        self.board.env[(2, 1)] = self.piece2
        self.board.env[(2, 2)] = self.piece3
        possible_actions = self.current_gs.generate_possible_actions()
        assert len(possible_actions) == self.current_gs.get_rep().get_dimensions()[0]*self.current_gs.get_rep()\
            .get_dimensions()[1] - 3
