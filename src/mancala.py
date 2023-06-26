from coliseum.examples.mancala.board_mancala import BoardMancala
from coliseum.examples.mancala.game_state_mancala import GameStateMancala
from coliseum.examples.mancala.master_mancala import MasterMancala
from coliseum.examples.mancala.player_mancala import PlayerMancala
from coliseum.player.player import LocalPlayerProxy


def run_multiple_games():
    for _ in range(1):
        player1 = LocalPlayerProxy(PlayerMancala(name="louis"))
        player2 = LocalPlayerProxy(PlayerMancala(name="loic"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        init_rep = BoardMancala()
        initial_game_state = GameStateMancala(init_scores, player1, list_players, init_rep)

        master = MasterMancala(name = "Mancala", initial_game_state = initial_game_state, players_iterator = list_players, log_file = "log.txt")
        master.record_game()

run_multiple_games()
