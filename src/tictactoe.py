from seahorse.examples.tictactoe.alpha_player_tictac import MyPlayer as AlphaPlayerTictac
from seahorse.examples.tictactoe.board_tictac import BoardTictac
from seahorse.examples.tictactoe.game_state_tictac import GameStateTictac
from seahorse.examples.tictactoe.master_tictac import MasterTictac
from seahorse.examples.tictactoe.player_tictac import PlayerTictac
from seahorse.examples.tictactoe.random_player_tictac import MyPlayer as RandomPlayerTictac
from seahorse.player.proxies import LocalPlayerProxy, RemotePlayerProxy


def run_multiple_games():
    for _ in range(1):
        player1 = LocalPlayerProxy(AlphaPlayerTictac("X", name="louis"),gs=GameStateTictac)
        player2 = RemotePlayerProxy(mimics=PlayerTictac,piece_type="O",name="jean")
        #player2 = LocalPlayerProxy(AlphaPlayerTictac("O", name="pierre"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        init_rep = BoardTictac(env={}, dim=[3, 3])
        initial_game_state = GameStateTictac(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep)

        master = MasterTictac(
            name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_file="log.txt", port=16001
        )
        master.record_game()

run_multiple_games()
