import json

from alpha_player_tictac import MyPlayer as AlphaPlayerTictac
from board_tictac import BoardTictac
from game_state_tictac import GameStateTictac
from loguru import logger
from master_tictac import MasterTictac
from player_tictac import PlayerTictac

from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster
from seahorse.player.player import Player
from seahorse.player.proxies import InteractivePlayerProxy, LocalPlayerProxy, RemotePlayerProxy


def run_multiple_games():
    for _ in range(1):
        player1 = AlphaPlayerTictac("X", name="louis")
        player2 = AlphaPlayerTictac("O", name="pierre")
        #player2 = RemotePlayerProxy(mimics=PlayerTictac,piece_type="O",name="jean")

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        init_rep = BoardTictac(env={}, dim=[3, 3])
        initial_game_state = GameStateTictac(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep)

        master = MasterTictac(
            name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_level="INFO", port=16001,
            n_listeners=0,
        )
        master.record_game()

run_multiple_games()
