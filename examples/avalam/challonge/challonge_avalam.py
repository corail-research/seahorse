import sys

from loguru import logger

from board_avalam import BoardAvalam, PieceAvalam
from game_state_avalam import GameStateAvalam
from master_avalam import MasterAvalam
from seahorse.player.proxies import LocalPlayerProxy

if __name__ == "__main__":
    args = sys.argv
    folder_player = str(args[1])
    p1 = str(args[2])
    p2 = str(args[3])
    port = int(args[4])
    player1_class = __import__(str(folder_player+p1), fromlist=[None])
    player2_class = __import__(str(folder_player+p2), fromlist=[None])
    player1 = LocalPlayerProxy(player1_class.MyPlayer("R", name=p1))
    player2 = LocalPlayerProxy(player2_class.MyPlayer("Y", name=p2))
    list_players = [player1, player2]
    init_scores = {player1.get_id(): 0, player2.get_id(): 0}
    dim = [9, 9]
    env = {}
    initial_board = [
        [0, 0, 1, -1, 0, 0, 0, 0, 0],
        [0, 1, -1, 1, -1, 0, 0, 0, 0],
        [0, -1, 1, -1, 1, -1, 1, 0, 0],
        [0, 1, -1, 1, -1, 1, -1, 1, -1],
        [1, -1, 1, -1, 0, -1, 1, -1, 1],
        [-1, 1, -1, 1, -1, 1, -1, 1, 0],
        [0, 0, 1, -1, 1, -1, 1, -1, 0],
        [0, 0, 0, 0, -1, 1, -1, 1, 0],
        [0, 0, 0, 0, 0, -1, 1, 0, 0],
    ]
    for i in range(dim[0]):
        for j in range(dim[1]):
            if initial_board[i][j] == 1:
                env[(i, j)] = PieceAvalam(piece_type=player1.get_piece_type(), owner=player1, value=1)
                init_scores[player1.get_id()] += 1
            elif initial_board[i][j] == -1:
                env[(i, j)] = PieceAvalam(piece_type=player2.get_piece_type(), owner=player2, value=1)
                init_scores[player2.get_id()] += 1
    init_rep = BoardAvalam(env=env, dim=dim)
    initial_game_state = GameStateAvalam(
        scores=init_scores, next_player=player1, players=list_players, rep=init_rep
    )

    master = MasterAvalam(
        name="Avalam", initial_game_state=initial_game_state, players_iterator=list_players, log_file="log.txt"
    )
    master.record_game()
    scores = master.get_scores()
    for key in scores.keys() :
        logger.info(f"{scores[key]},")
    logger.info(f"{master.get_winner()[0].get_name()}")
