import argparse
import asyncio
import os
from os.path import basename, splitext, dirname
import platform
import sys

from loguru import logger
from board_tictac import BoardTictac
from player_tictac import PlayerTictac
from master_tictac import MasterTictac
from game_state_tictac import GameStateTictac
from seahorse.player.proxies import InteractivePlayerProxy, LocalPlayerProxy, RemotePlayerProxy
from seahorse.utils.gui_client import GUIClient
from seahorse.utils.recorders import StateRecorder

def play(player1, player2, log_level, port, gui, gui_path, record, address) :
    list_players = [player1, player2]
    init_scores = {player1.get_id(): 0, player2.get_id(): 0}
    init_rep = BoardTictac(env={}, dim=[3, 3])
    initial_game_state = GameStateTictac(
        scores=init_scores, next_player=player1, players=list_players, rep=init_rep)
    master = MasterTictac(
        name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_level=log_level, port=port, hostname=address
    )
    listeners = [GUIClient(path=gui_path)]*gui
    if record :
        listeners.append(StateRecorder())
    master.record_game(listeners=listeners)

if __name__=="__main__":

    parser = argparse.ArgumentParser(
                        prog="main_abalone.py",
                        description="Description of the different execution modes:",
                        epilog='''
  ___           _                    
 / __| ___ __ _| |_  ___ _ _ ___ ___ 
 \__ \/ -_) _` | ' \/ _ \ '_(_-</ -_)
 |___/\___\__,_|_||_\___/_| /__/\___|
                                     ''',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t","--type",
                        required=True,
                        type=str, 
                        choices=["local", "host_game", "connect", "human_vs_computer", "human_vs_human"],
                        help="\nThe execution mode you want.\n" 
                             +" - local: Runs everything on you machine\n"
                             +" - host_game: Runs a single player on your machine and waits for an opponent to connect with the 'connect' node.\n\t      You must provide an external ip for the -a argument (use 'ipconfig').\n"
                             +" - connect: Runs a single player and connects to a distant game launched with the 'host' at the hostname specified with '-a'.\n"
                             +" - human_vs_computer: Launches a GUI locally for you to challenge your player.\n"
                             +" - human_vs_human: Launches two GUIs locally for you to experiment the game's mechanics.\n"
                             +"\n"
                        )
    parser.add_argument("-c","--config",required=False,choices=["classic","alien"], default="classic",help="\nSets the starting board configuration.")
    parser.add_argument("-a","--address",required=False, default="localhost",help="\nThe external ip of the machine that hosts the GameMaster.\n\n")
    parser.add_argument("-p","--port",required=False,type=int, default=16001, help="The port of the machine that hosts the GameMaster.\n\n")
    parser.add_argument("-g","--no-gui",action='store_false',default=True, help="Headless mode\n\n")
    parser.add_argument("-r","--record",action="store_true",default=False, help="Stores the succesive game states in a json file.\n\n")
    parser.add_argument("-l","--log",required=False,choices=["DEBUG","INFO"], default="DEBUG",help="\nSets the logging level.")
    parser.add_argument("players_list",nargs="*", help='The players')
    args=parser.parse_args()

    type = vars(args).get("type")
    address = vars(args).get("address")
    port = vars(args).get("port")
    gui = vars(args).get("no_gui")
    record = vars(args).get("record")
    log_level = vars(args).get("log")
    list_players = vars(args).get("players_list")

    gui_path = os.path.join(dirname(os.path.abspath(__file__)),'GUI','index.html')

    if type == "local" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        folder = dirname(list_players[1])
        sys.path.append(folder)
        player2_class = __import__(splitext(basename(list_players[1]))[0], fromlist=[None])
        player1 = player1_class.MyPlayer("X", name=splitext(basename(list_players[0]))[0]+"_1")
        player2 = player2_class.MyPlayer("O", name=splitext(basename(list_players[1]))[0]+"_2")
        play(player1=player1, player2=player2, log_level=log_level, port=port, address=address, gui=gui, record=record, gui_path=gui_path)
    elif type == "host_game" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        player1 = LocalPlayerProxy(player1_class.MyPlayer("X", name=splitext(basename(list_players[0]))[0]+"_local"),gs=GameStateTictac)
        player2 = RemotePlayerProxy(mimics=PlayerTictac,piece_type="O",name="_remote")
        if address=='localhost':
            logger.warning('Using `localhost` with `host_game` mode, if both players are on different machines')
            logger.warning('use ipconfig/ifconfig to get your external ip and specity this with -a')
        play(player1=player1, player2=player2, log_level=log_level, port=port, address=address, gui=int(gui)+1, record=record, gui_path=gui_path)
    elif type == "connect" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player2_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        player2 = LocalPlayerProxy(player2_class.MyPlayer("O", name="_remote"),gs=GameStateTictac)
        if address=='localhost':
            logger.warning('Using `localhost` with `connect` mode, if both players are on different machines')
            logger.warning('use ipconfig/ifconfig to get your external ip and specity this with -a')
        asyncio.new_event_loop().run_until_complete(player2.listen(keep_alive=True,master_address=f"http://{address}:{port}"))
    elif type == "human_vs_computer" :
        folder = dirname(list_players[0])
        sys.path.append(folder)
        player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        player1 = InteractivePlayerProxy(PlayerTictac("X", name="bob"),gui_path=gui_path,gs=GameStateTictac)
        player2 = LocalPlayerProxy(player1_class.MyPlayer("O", name=splitext(basename(list_players[0]))[0]),gs=GameStateTictac)
        play(player1=player1, player2=player2, log_level=log_level, port=port, address=address, gui=False, record=record, gui_path=gui_path)
    elif type == "human_vs_human" :
        player1 = InteractivePlayerProxy(PlayerTictac("X", name="bob"),gui_path=gui_path,gs=GameStateTictac)
        player2 = InteractivePlayerProxy(PlayerTictac("O", name="alice"),gui_path=gui_path,gs=GameStateTictac)
        play(player1=player1, player2=player2, log_level=log_level, port=port, address=address, gui=False, record=record, gui_path=gui_path)
        
