import unittest

from seahorse.examples.tictactoe.board_tictac import BoardTictac
from seahorse.examples.tictactoe.game_state_tictac import GameStateTictac
from seahorse.examples.tictactoe.master_tictac import MasterTictac
from seahorse.examples.tictactoe.random_player_tictac import PlayerTictac
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece


class TicTacToeRegularTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.player1 = PlayerTictac("X", name="louis")
        self.player2 = PlayerTictac("O", name="loic")
        self.list_players = [self.player1, self.player2]
        self.init_scores = {self.player1.get_id(): 0, self.player2.get_id(): 0}
        self.init_rep = BoardTictac(env={}, dim=[3, 3])
        self.initial_game_state = GameStateTictac(
            scores=self.init_scores, next_player=self.player1, players=self.list_players, rep=self.init_rep)

        self.master = MasterTictac(
            name="Tic-Tac-Toe", initial_game_state=self.initial_game_state, players_iterator=self.list_players, log_file="log.txt"
        )

        self.winning_configurations = [[(i, j) for i in range(3)] for j in range(3)] + \
            [[(j, i) for i in range(3)] for j in range(3)] + \
            [[(i, i) for i in range(3)]] +\
            [[(i, 2-i) for i in range(3)]]

        self.non_winning_configurations = [[(i, j) for i in range(2)] for j in range(3)] + \
            [[(j, i) for i in range(2)] for j in range(3)] + \
            [[(i, i) for i in [2, 2, 1]]] +\
            [[(i, 1-i) for i in [1, 1, 0]]]

        return super().setUp()

    def test_tictactoe_sequential_turns(self):
        """
            Ensures that a different player is playing at each turn
        """
        current_player_id = self.list_players[0].id_player
        while True:
            next_state = self.master.step()
            if next_state.is_done():
                break
            next_id = next_state.get_next_player().id_player
            assert next_id != current_player_id
            current_player_id = next_id
            self.master.current_game_state = next_state

    def test_tictactoe_less_than_9_steps(self):
        """
            Ensures the game has a normal number of steps
        """
        nsteps = 0
        curr_state = self.initial_game_state
        while not curr_state.is_done():
            nsteps += 1
            curr_state = self.master.step()
            self.master.current_game_state = curr_state
        assert nsteps <= 9

    def test_has_won(self):
        """
            Ensures the has_won method is correct
        """

        for x, z in zip(self.winning_configurations, self.non_winning_configurations):
            phony_winning_board = BoardTictac(env={
                w: Piece("X", self.player1) for w in x
            }, dim=[3, 3])

            phony_non_winning_board = BoardTictac(env={
                w: Piece("X", self.player1) for w in z
            }, dim=[3, 3])

            phony_w_game_state = GameStateTictac(
                scores=self.init_scores, next_player=self.player1, players=self.list_players, rep=phony_winning_board)
            phony_nw_game_state = GameStateTictac(
                scores=self.init_scores, next_player=self.player1, players=self.list_players, rep=phony_non_winning_board)

            assert phony_w_game_state.has_won()
            assert not phony_nw_game_state.has_won()
            assert phony_w_game_state.is_done()
            assert not phony_nw_game_state.is_done()

    def test_check_action(self):
        """
            Ensures illegal actions are caught properly
        """
        original_repr = BoardTictac(env={
            (0, 0): Piece("X", self.player1)
        }, dim=[3, 3])

        phony_game_state = GameStateTictac(
            {}, next_player=self.player2, players=self.list_players, rep=original_repr)

        type_change_repr = BoardTictac(env={
            (0, 0): Piece("O", self.player1)
        }, dim=[3, 3])
        owner_change_repr = BoardTictac(env={
            (0, 0): Piece("X", self.player2)
        }, dim=[3, 3])
        removed_change_repr = BoardTictac(env={}, dim=[3, 3])

        valid_change_repr = BoardTictac(env={
            (0, 0): Piece("X", self.player1),
            (1, 1): Piece("O", self.player2)
        }, dim=[3, 3])

        illegal_states = [type_change_repr, owner_change_repr,
                          removed_change_repr, original_repr]
        legit_states = [valid_change_repr]

        illegal_actions = [Action(original_repr, x) for x in illegal_states]
        legit_actions = [Action(original_repr, x) for x in legit_states]

        for x in illegal_actions:
            assert not phony_game_state.check_action(x)

        for x in legit_actions:
            assert phony_game_state.check_action(x)

    def tearDown(self) -> None:
        return super().tearDown()
