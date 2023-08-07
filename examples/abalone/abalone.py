import json

from loguru import logger
from alpha_player_abalone import MyPlayer as AlphaPlayerAbalone
from board_abalone import BoardAbalone
from game_state_abalone import GameStateAbalone
from master_abalone import MasterAbalone
from player_abalone import PlayerAbalone
from random_player_abalone import MyPlayer as RandomPlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster
from seahorse.player.player import Player
from seahorse.player.proxies import LocalPlayerProxy, RemotePlayerProxy, InteractivePlayerProxy

W = 1
B = 2

def run_multiple_games():
    for _ in range(1):

        player2 = RemotePlayerProxy(mimics=PlayerAbalone,piece_type="W",name="marcel")
        player1 = InteractivePlayerProxy(AlphaPlayerAbalone(piece_type="B"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        logger.info(f"init_scores{ init_scores}")
        dim = [17, 9]
        env = {}
        # 0 case non accessible
        # 1 case player 1
        # 2 case player 2
        # 3 case vide accessible
        # CLASSIQUE
        # initial_board = [
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        #     [0, 0, 0, 1, 0, 1, 0, 0, 0],
        #     [0, 0, 1, 0, 1, 0, 3, 0, 0],
        #     [0, 1, 0, 1, 0, 3, 0, 3, 0],
        #     [1, 0, 1, 0, 1, 0, 3, 0, 3],
        #     [0, 1, 0, 1, 0, 3, 0, 3, 0],
        #     [1, 0, 1, 0, 3, 0, 3, 0, 3],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [3, 0, 3, 0, 3, 0, 3, 0, 3],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [3, 0, 3, 0, 3, 0, 2, 0, 2],
        #     [0, 3, 0, 3, 0, 2, 0, 2, 0],
        #     [3, 0, 3, 0, 2, 0, 2, 0, 2],
        #     [0, 3, 0, 3, 0, 2, 0, 2, 0],
        #     [0, 0, 3, 0, 2, 0, 2, 0, 0],
        #     [0, 0, 0, 2, 0, 2, 0, 0, 0],
        #     [0, 0, 0, 0, 2, 0, 0, 0, 0],
        # ]
        # MARGUERITE
        # initial_board = [
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        #     [0, 0, 0, 1, 0, 1, 0, 0, 0],
        #     [0, 0, 3, 0, 1, 0, 3, 0, 0],
        #     [0, 2, 0, 1, 0, 1, 0, 3, 0],
        #     [2, 0, 2, 0, 1, 0, 3, 0, 3],
        #     [0, 2, 0, 3, 0, 3, 0, 3, 0],
        #     [2, 0, 2, 0, 3, 0, 3, 0, 3],
        #     [0, 2, 0, 3, 0, 3, 0, 3, 0],
        #     [3, 0, 3, 0, 3, 0, 3, 0, 3],
        #     [0, 3, 0, 3, 0, 3, 0, 2, 0],
        #     [3, 0, 3, 0, 3, 0, 2, 0, 2],
        #     [0, 3, 0, 3, 0, 3, 0, 2, 0],
        #     [3, 0, 3, 0, 1, 0, 2, 0, 2],
        #     [0, 3, 0, 1, 0, 1, 0, 2, 0],
        #     [0, 0, 3, 0, 1, 0, 3, 0, 0],
        #     [0, 0, 0, 1, 0, 1, 0, 0, 0],
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        # ]
        # ALIEN
        initial_board = [
             [0, 0, 0, 0, 2, 0, 0, 0, 0],
             [0, 0, 0, 3, 0, 3, 0, 0, 0],
             [0, 0, 2, 0, 2, 0, 3, 0, 0],
             [0, 3, 0, 1, 0, 2, 0, 3, 0],
             [2, 0, 1, 0, 1, 0, 3, 0, 3],
             [0, 2, 0, 2, 0, 3, 0, 3, 0],
             [3, 0, 1, 0, 2, 0, 3, 0, 3],
             [0, 2, 0, 2, 0, 3, 0, 3, 0],
             [3, 0, 3, 0, 3, 0, 3, 0, 3],
             [0, 3, 0, 3, 0, 1, 0, 1, 0],
             [3, 0, 3, 0, 1, 0, 2, 0, 3],
             [0, 3, 0, 3, 0, 1, 0, 1, 0],
             [3, 0, 3, 0, 2, 0, 2, 0, 1],
             [0, 3, 0, 1, 0, 2, 0, 3, 0],
             [0, 0, 3, 0, 1, 0, 1, 0, 0],
             [0, 0, 0, 3, 0, 3, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 0],
         ]
        # ETOILE
        # initial_board = [
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        #     [0, 0, 0, 3, 0, 3, 0, 0, 0],
        #     [0, 0, 3, 0, 1, 0, 3, 0, 0],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [1, 0, 3, 0, 1, 0, 3, 0, 1],
        #     [0, 1, 0, 3, 0, 1, 0, 1, 0],
        #     [3, 0, 1, 0, 1, 0, 1, 0, 3],
        #     [0, 3, 0, 1, 0, 1, 0, 3, 0],
        #     [3, 0, 1, 0, 3, 0, 2, 0, 3],
        #     [0, 3, 0, 2, 0, 2, 0, 3, 0],
        #     [3, 0, 2, 0, 2, 0, 2, 0, 3],
        #     [0, 2, 0, 2, 0, 3, 0, 2, 0],
        #     [2, 0, 3, 0, 2, 0, 3, 0, 2],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [0, 0, 3, 0, 2, 0, 3, 0, 0],
        #     [0, 0, 0, 3, 0, 3, 0, 0, 0],
        #     [0, 0, 0, 0, 2, 0, 0, 0, 0],
        # ]
        for i in range(dim[0]):
            for j in range(dim[1]):
                if initial_board[i][j] == W:
                    env[(i, j)] = Piece(piece_type=player1.get_piece_type(), owner=player1)
                elif initial_board[i][j] == B:
                    env[(i, j)] = Piece(piece_type=player2.get_piece_type(), owner=player2)
        init_rep = BoardAbalone(env=env, dim=dim)
        initial_game_state = GameStateAbalone(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep, step=0
        )

        master = MasterAbalone(
             name="Abalone", initial_game_state=initial_game_state, players_iterator=list_players, log_level="INFO", port=16001
         )
        master.record_game()

run_multiple_games()
