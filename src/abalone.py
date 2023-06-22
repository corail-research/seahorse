from coliseum.examples.abalone.alpha_player_abalone import AlphaPlayerAbalone
from coliseum.examples.abalone.board_abalone import BoardAbalone
from coliseum.examples.abalone.game_state_abalone import GameStateAbalone
from coliseum.examples.abalone.master_abalone import MasterAbalone
from coliseum.examples.abalone.random_player_abalone import RandomPlayerAbalone
from coliseum.game.game_layout.board import Piece
from coliseum.player.player import LocalPlayerProxy


def run_multiple_games():
    for _ in range(1):
        player1 = LocalPlayerProxy(RandomPlayerAbalone("W", name="louis"))
        player2 = LocalPlayerProxy(AlphaPlayerAbalone("B", name="loic"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        dim = [17, 9]
        env = {}
        # 0 case non accessible
        # 1 case player 1
        # 2 case player 2
        # 3 case vide accessible
        initial_board = [
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 3, 0, 0],
            [0, 1, 0, 1, 0, 3, 0, 3, 0],
            [1, 0, 1, 0, 1, 0, 3, 0, 3],
            [0, 1, 0, 1, 0, 3, 0, 3, 0],
            [1, 0, 1, 0, 3, 0, 3, 0, 3],
            [0, 3, 0, 3, 0, 3, 0, 3, 0],
            [3, 0, 3, 0, 3, 0, 3, 0, 3],
            [0, 3, 0, 3, 0, 3, 0, 3, 0],
            [3, 0, 3, 0, 3, 0, 2, 0, 2],
            [0, 3, 0, 3, 0, 2, 0, 2, 0],
            [3, 0, 3, 0, 2, 0, 2, 0, 2],
            [0, 3, 0, 3, 0, 2, 0, 2, 0],
            [0, 0, 3, 0, 2, 0, 2, 0, 0],
            [0, 0, 0, 2, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 2, 0, 0, 0, 0],
        ]
        for i in range(dim[0]):
            for j in range(dim[1]):
                if initial_board[i][j] == 1:
                    env[(i, j)] = Piece(piece_type=player1.get_piece_type(), owner=player1)
                elif initial_board[i][j] == 2:
                    env[(i, j)] = Piece(piece_type=player2.get_piece_type(), owner=player2)
        init_rep = BoardAbalone(env=env, dim=dim)
        initial_game_state = GameStateAbalone(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep
        )

        master = MasterAbalone(
            name="Abalone", initial_game_state=initial_game_state, players_iterator=list_players, log_file="log.txt"
        )
        master.record_game()


run_multiple_games()
