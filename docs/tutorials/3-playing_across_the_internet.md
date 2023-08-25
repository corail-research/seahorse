#3 - Playing across the internet
Several mode of executions are possible with our previous implementation of tic-tac-toe.
Below is an example of a main file.

First, we define a play function which will be used in all the modes.
```py

import argparse
import asyncio
import os
from os.path import basename, splitext, dirname
import sys
from board_tictac import BoardTictac
from player_tictac import PlayerTictac
from master_tictac import MasterTictac
from game_state_tictac import GameStateTictac
from seahorse.player.proxies import InteractivePlayerProxy, LocalPlayerProxy, RemotePlayerProxy
from seahorse.utils.gui_client import GUIClient
from seahorse.utils.recorders import StateRecorder

def play(player1, player2, log_level, port, gui, gui_dist, gui_path, record, address) :
    list_players = [player1, player2]
    init_scores = {player1.get_id(): 0, player2.get_id(): 0}
    init_rep = BoardTictac(env={}, dim=[3, 3])
    initial_game_state = GameStateTictac(
        scores=init_scores, next_player=player1, players=list_players, rep=init_rep)
    master = MasterTictac(
        name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_level=log_level, port=port, hostname=address
    )
    listeners = [GUIClient(path=gui_path)]*gui+[GUIClient()]*gui_dist
    if record :
        listeners.append(StateRecorder())
    master.record_game(listeners=listeners)
```
Let's now implement a parser to easily launch our program with command line.
```py
if __name__=="__main__":
    parser = argparse.ArgumentParser(
                        prog="Launcher",
                        description="What the program does",
                        epilog="Text at the bottom of help")
    parser.add_argument("-t","--type",required=True,type=str, choices=["local", "remote", "standalone", "humvscomp", "humvshum"])
    parser.add_argument("-n","--nb_players",required=False,type=int, default=2)
    parser.add_argument("-add","--address",required=False, default="localhost")
    parser.add_argument("-p","--port",required=False,type=int, default=16001)
    parser.add_argument("-g","--gui",required=False,type=int, default=0)
    parser.add_argument("-gd","--gui_dist",required=False,type=int, default=0)
    parser.add_argument("-gp","--gui_path",required=False,type=str, default=os.path.join("GUI","index.html"))
    parser.add_argument("-r","--record",action="store_true",default=False)
    parser.add_argument("-l","--log",required=False,choices=["DEBUG","INFO"], default="INFO")
    parser.add_argument("list_players",nargs="*")
    args=parser.parse_args()
    
    type = vars(args).get("type")
    nb_players = vars(args).get("nb_players")
    address = vars(args).get("address")
    port = vars(args).get("port")
    gui = vars(args).get("gui")
    gui_dist = vars(args).get("gui_dist")
    gui_path = vars(args).get("gui_path")
    record = vars(args).get("record")
    log_level = vars(args).get("log")
    list_players = vars(args).get("list_players")
    
    if type == "local" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        folder = dirname(list_players[1])
        sys.path.append(folder)
        player2_class = __import__(splitext(basename(list_players[1]))[0], fromlist=[None])
        player1 = player1_class.MyPlayer("X", name=splitext(basename(list_players[0]))[0])
        player2 = player2_class.MyPlayer("O", name=splitext(basename(list_players[1]))[0])
        play(player1=player1, player2=player2, log_level=log_level, port=port, gui=gui, gui_dist=gui_dist, gui_path=gui_path, record=record, address=address)
    elif type == "remote" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        player1 = LocalPlayerProxy(player1_class.MyPlayer("X", name=splitext(basename(list_players[0]))[0]),gs=GameStateTictac)
        player2 = RemotePlayerProxy(mimics=PlayerTictac,piece_type="O",name=splitext(basename(list_players[1]))[0])
        play(player1=player1, player2=player2, log_level=log_level, port=port, gui=gui, gui_dist=gui_dist, gui_path=gui_path, record=record, address=address)
    elif type == "standalone" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player2_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        player2 = LocalPlayerProxy(player2_class.MyPlayer("O", name=splitext(basename(list_players[0]))[0]),gs=GameStateTictac)
        asyncio.new_event_loop().run_until_complete(player2.listen(keep_alive=True,master_address=f"http://{address}:{port}"))
    elif type == "humvscomp" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        player1 = InteractivePlayerProxy(PlayerTictac("X", name="bob"),gui_path=gui_path,gs=GameStateTictac)
        player2 = LocalPlayerProxy(player1_class.MyPlayer("O", name=splitext(basename(list_players[0]))[0]),gs=GameStateTictac)
        play(player1=player1, player2=player2, log_level=log_level, port=port, gui=0, gui_dist=gui_dist, gui_path=gui_path, record=record, address=address)
    elif type == "humvshum" :
        player1 = InteractivePlayerProxy(PlayerTictac("X", name="bob"),gui_path=gui_path,gs=GameStateTictac)
        player2 = InteractivePlayerProxy(PlayerTictac("O", name="alice"),gs=GameStateTictac)
        play(player1=player1, player2=player2, log_level=log_level, port=port, gui=0, gui_dist=gui_dist, gui_path=gui_path, record=record, address=address)
        
```
