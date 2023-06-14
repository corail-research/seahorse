import asyncio
import time
from coliseum.examples.tictactoe.alpha_player_tictac import AlphaPlayerTictac
from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.examples.tictactoe.game_state_tictac import GameStateTictac
from coliseum.examples.tictactoe.master_tictac import MasterTictac
from coliseum.examples.tictactoe.random_player_tictac import RandomPlayerTictac
from coliseum.player.player import LocalPlayerProxy, RemotePlayerProxy

def run_multiple_games():
    for _ in range(2):
        player1 = LocalPlayerProxy(AlphaPlayerTictac("X", name="louis"))

        player2 = LocalPlayerProxy(AlphaPlayerTictac("O", name="loic"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        init_rep = BoardTictac(env={}, dim=[3, 3])
        initial_game_state = GameStateTictac(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep)

        master = MasterTictac(
            name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_file="log.txt"
        )
        master.record_game()


run_multiple_games()
