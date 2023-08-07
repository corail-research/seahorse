import sys

from loguru import logger

from board_abalone import BoardAbalone
from game_state_abalone import GameStateAbalone
from master_abalone import MasterAbalone
from seahorse.game.game_layout.board import Piece
from seahorse.player.proxies import LocalPlayerProxy

if __name__ == "__main__":
    args = sys.argv
    folder_player = str(args[1])
    p1 = str(args[2])
    p2 = str(args[3])
    port = int(args[4])
    player1_class = __import__(str(folder_player+p1), fromlist=[None])
    player2_class = __import__(str(folder_player+p2), fromlist=[None])
    player1 = LocalPlayerProxy(player1_class.MyPlayer("W", name=p1))
    player2 = LocalPlayerProxy(player2_class.MyPlayer("B", name=p2))

    list_players = [player1, player2]
    init_scores = {player1.get_id(): 0, player2.get_id(): 0}
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
    W = 1
    B = 2
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
            name="Abalone", initial_game_state=initial_game_state, players_iterator=list_players, log_level="INFO"
        )
    master.record_game()
    scores = master.get_scores()
    invert_list = []
    for key in scores.keys() :
        invert_list.append(abs(scores[key]))
    for i in range(len(invert_list)-1,-1,-1) :
        logger.info(f"{invert_list[i]},")
    logger.info(master.get_winner()[0].get_name())
