import random
from typing import Callable, List, Dict
import unittest
from coliseum.game.action import Action

from coliseum.game.game_state import GameState
from coliseum.game.master import GameMaster
from coliseum.game.representation import Representation

from coliseum.player.player import Player


class RandomPlayerIterator:
    def __init__(self, players: List[Player]):
        self.players = players

    def __iter__(self):
        self.current_player = self.players[random.randint(
            0, len(self.players))]
        return self

    def __next__(self):
        return self.players[random.randint(0, len(self.players)-1)]


class PlayerStub(Player):
    def solve(self, current_rep: Representation, **kwargs) -> Representation:
        return current_rep

    def check_action(self, action: Action) -> bool:
        return True


class GameMasterStub(GameMaster):
    def compute_scores(self, representation: Representation) -> List[float]:
        return {x.get_id(): 1 for x in self.players}


class GameStateStub(GameState):
    def is_done(self) -> bool:
        return False


class MasterTestCase(unittest.TestCase):

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
                rep=Representation(None)
            ),
            log_file=""
        )
        for _ in range(10):
            new_state = m.step()
            assert new_state.get_next_player().name in [
                "bob", "jean", "marcel"]
