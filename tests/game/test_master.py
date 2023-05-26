import random
import unittest
from typing import Dict, List, Set

from coliseum.game.action import Action
from coliseum.game.game_layout.board import Board
from coliseum.game.game_state import GameState
from coliseum.game.master import GameMaster
from coliseum.player.player import Player


class RandomPlayerIterator:
    def __init__(self, players: List[Player]):
        self.players = players

    def __iter__(self):
        self.current_player = self.players[random.randint(
            0, len(self.players))]
        return self

    def __next__(self):
        return self.players[random.randint(0, len(self.players) - 1)]


class PlayerStub(Player):
    def solve(self, possible_actions: Set[Board], **kwargs) -> Board:
        if kwargs:
            pass
        return list(possible_actions)[0].get_new_rep()


class GameMasterStub(GameMaster):
    def compute_scores(self, representation: Board) -> Dict[int, float]:
        if representation:
            pass
        return {x.get_id(): 1 for x in self.players}


class GameStateStub(GameState):
    def is_done(self) -> bool:
        return False

    def check_action(self, action: Action) -> bool:
        if action:
            pass
        return True

    def generate_possible_actions(self) -> Set[Action]:
        return {Action(Board({}, 0), Board({}, 0))}


class MasterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_step(self):
        players_list = [PlayerStub("bob"), PlayerStub(
            "marcel"), PlayerStub("jean")]
        players_iter = RandomPlayerIterator(players=players_list)
        m = GameMasterStub(
            name="julie",
            players_iterator=players_iter,
            initial_game_state=GameStateStub(
                scores={x.get_id(): 1 for x in players_list},
                next_player=next(players_iter),
                players=players_list,
                rep=Board({}, 0),
            ),
            log_file="",
        )
        for _ in range(10):
            new_state = m.step()
            assert new_state.get_next_player().name in [
                "bob", "jean", "marcel"]
