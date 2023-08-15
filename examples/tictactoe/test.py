import argparse
from os.path import basename, splitext
from board_tictac import BoardTictac
from master_tictac import MasterTictac
from game_state_tictac import GameStateTictac


if __name__=="__main__":
    parser = argparse.ArgumentParser(
                        prog="Launcher",
                        description="What the program does",
                        epilog="Text at the bottom of help")
    parser.add_argument("-t","--type",required=True,type=str, choices=["local", "remote", "humvscomp", "humvshum"])
    parser.add_argument("-n","--nb_players",required=True,type=int)
    parser.add_argument("-add","--address",required=False)
    parser.add_argument("-p","--port",required=False,type=int)
    parser.add_argument("-g","--gui",required=False,type=int)
    parser.add_argument("-l","--log",required=False,choices=["DEBUG","INFO"])
    parser.add_argument("list_players",nargs="*")
    args=parser.parse_args()
    
    type = vars(args).get("type")
    nb_players = vars(args).get("nb_players")
    address = vars(args).get("address") if vars(args).get("address") is not None else "localhost"
    port = vars(args).get("port") if vars(args).get("port") is not None else 16001
    gui = vars(args).get("gui") if vars(args).get("gui") is not None else 0
    log_level = vars(args).get("log") if vars(args).get("log") is not None else "INFO"
    list_players = vars(args).get("list_players")
    
    print(type, nb_players, address, port, gui, list_players)
    
    if type == "local" :
        player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
        player2_class = __import__(splitext(basename(list_players[1]))[0], fromlist=[None])
        player1 = player1_class.MyPlayer("X", name=splitext(basename(list_players[0]))[0])
        player2 = player2_class.MyPlayer("O", name=splitext(basename(list_players[1]))[0])
        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        init_rep = BoardTictac(env={}, dim=[3, 3])
        initial_game_state = GameStateTictac(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep)
        master = MasterTictac(
            name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_level=log_level, port=port, n_listeners=gui,
        )
        master.record_game()
    elif type == "remote" :
        print("ok2")
    elif type == "humvscomp" :
        print("ok3")
    elif type == "humvshum" :
        print("ok4")
        
