import asyncio
import sys 
import argparse
import subprocess
import os
import json
from seahorse.examples.abalone import alpha_player_abalone
from seahorse.examples.abalone.board_abalone import BoardAbalone
from seahorse.examples.abalone.game_state_abalone import GameStateAbalone
from seahorse.examples.abalone.master_abalone import MasterAbalone
from seahorse.examples.tictactoe.alpha_player_tictac import MyPlayer as AlphaPlayerTictac
from seahorse.examples.tictactoe.board_tictac import BoardTictac
from seahorse.examples.tictactoe.game_state_tictac import GameStateTictac
from seahorse.examples.tictactoe.master_tictac import MasterTictac
from seahorse.examples.tictactoe.player_tictac import PlayerTictac
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster
from seahorse.player.player import Player
from seahorse.player.proxies import LocalPlayerProxy, RemotePlayerProxy, InteractivePlayerProxy
from seahorse.examples.abalone.random_player_abalone import MyPlayer as RandomPlayerAbalone
from seahorse.examples.abalone.alpha_player_abalone import MyPlayer as AlphaPlayerAbalone

W = 1
B = 2
def open_webpage(url):
    try:
        os.startfile(url)
    except AttributeError:
        try:
            subprocess.call(['open', url])
        except:
            print('Could not open URL')

def tictactoe(args):
    if args.remote:
        pass
    else:
        open_webpage('/'.join(["file://"]+os.path.abspath(__file__).split("/")[:-1]+["seahorse/execution/web/examples/tictactoe/index.html"]))
        player1 = LocalPlayerProxy(AlphaPlayerTictac("X", name="louis"),gs=GameStateTictac)
        player2 = InteractivePlayerProxy(PlayerTictac("O", name="pierre"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        init_rep = BoardTictac(env={}, dim=[3, 3])
        initial_game_state = GameStateTictac(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep)

        master = MasterTictac(
            name="Tic-Tac-Toe", 
            initial_game_state=initial_game_state, 
            players_iterator=list_players, 
            log_file="log.txt", 
            port=args.port,
            hostname=args.address,
            n_listeners=args.listeners
        )
        master.record_game()

def abalone(args):
    if args.remote:
        open_webpage('/'.join(["file://"]+os.path.abspath(__file__).split("/")[:-1]+["seahorse/execution/web/examples/abalone/interactive/index.html"]))

        player1 = LocalPlayerProxy(AlphaPlayerAbalone(piece_type="W", name= "marcel"),masterless=True,gs=GameStateAbalone)
        asyncio.new_event_loop().run_until_complete(player1.listen(keep_alive=True,master_address=f"http://{args.address}:{args.port}"))
    else:
        open_webpage('/'.join(["file://"]+os.path.abspath(__file__).split("/")[:-1]+["seahorse/execution/web/examples/abalone/interactive/index.html"]))

        player2 = RemotePlayerProxy(mimics=RandomPlayerAbalone,piece_type="W",name="marcel")
        player1 = InteractivePlayerProxy(AlphaPlayerAbalone(piece_type="B"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        print("init_scores", init_scores)
        dim = [17, 9]
        env = {}
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
             name="Abalone",
             initial_game_state=initial_game_state,
             players_iterator=list_players, 
             log_file="log.txt", 
             port=args.port,
             hostname=args.address,
             n_listeners=args.listeners
         )
        master.record_game()

if __name__=="__main__":

    parser = argparse.ArgumentParser(
                        prog='Launcher',
                        description='What the program does',
                        epilog='Text at the bottom of help')
    parser.add_argument('-p','--port',required=True,type=int)
    parser.add_argument('-a','--address',required=True)
    parser.add_argument('-r','--remote',required=False,action='store_true')
    parser.add_argument('-l','--listeners',required=False,type=int)
    parser.add_argument('-g','--game',required=True,choices=['tictactoe','abalone','avalam'])
    args=parser.parse_args()

    if args.game=="tictactoe":
        tictactoe(args)
    elif args.game=="abalone":
        abalone(args)
    



