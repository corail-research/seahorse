from alpha_player_avalam import MyPlayer as AlphaPlayerAvalam
from board_avalam import BoardAvalam, PieceAvalam
from game_state_avalam import GameStateAvalam
from master_avalam import MasterAvalam
from player_avalam import PlayerAvalam
from random_player_avalam import MyPlayer as RandomPlayerAvalam
from seahorse.player.proxies import LocalPlayerProxy, RemotePlayerProxy


def run_multiple_games():
    for _ in range(1):
        player1 = LocalPlayerProxy(AlphaPlayerAvalam("Y", name="louis"))
        player2 = RemotePlayerProxy(mimics=PlayerAvalam,piece_type="R",name="bob")

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
            name="Avalam", initial_game_state=initial_game_state, players_iterator=list_players, log_level="INFO", port=16001
        )
        master.record_game()

run_multiple_games()
