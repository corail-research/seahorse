import sys

from board_tictac import BoardTictac
from game_state_tictac import GameStateTictac
from loguru import logger
from master_tictac import MasterTictac

from seahorse.player.proxies import LocalPlayerProxy

if __name__ == "__main__":
    args = sys.argv
    folder_player = str(args[1])
    if folder_player == "." :
        folder_player=""
    p1 = str(args[2])
    p2 = str(args[3])
    port = int(args[4])
    player1_class = __import__(str(folder_player+p1), fromlist=[None])
    player2_class = __import__(str(folder_player+p2), fromlist=[None])
    player1 = player1_class.MyPlayer("X", name=p1)
    player2 = player2_class.MyPlayer("O", name=p2)
    list_players = [player1, player2]
    init_scores = {player1.get_id(): 0, player2.get_id(): 0}
    init_rep = BoardTictac(env={}, dim=[3, 3])
    initial_game_state = GameStateTictac(
        scores=init_scores, next_player=player1, players=list_players, rep=init_rep)
    master = MasterTictac(
        name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_level="INFO", port=port
    )
    master.record_game()
