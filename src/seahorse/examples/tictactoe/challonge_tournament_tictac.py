from seahorse.examples.tictactoe.board_tictac import BoardTictac
from seahorse.examples.tictactoe.game_state_tictac import GameStateTictac
from seahorse.examples.tictactoe.master_tictac import MasterTictac
from seahorse.player.player import LocalPlayerProxy
from seahorse.tournament.challonge_tournament import ChallongeTournament


class ChallongeTournamentTictac(ChallongeTournament) :

    def __init__(self, id_challonge, keypass_challonge, folder_player, log_file=None) -> None:
        super().__init__(id_challonge, keypass_challonge, folder_player, log_file)

    def build_initial_rep(self):
        return BoardTictac(env={}, dim=[3, 3])

    def build_initial_scores(self, p1, p2):
        return {p1.get_id(): 0, p2.get_id(): 0}

    def build_initial_game_state(self, p1, p2, scores, rep):
        return GameStateTictac(scores=scores, next_player=p1, players=[p1,p2], rep=rep)

    def build_initial_master(self, p1, p2, game_state):
        return MasterTictac(name="Tic-Tac-Toe", initial_game_state=game_state, players_iterator=[p1,p2], log_file=self.log_file)

    def build_players(self, p1, p2, folder_player) :
        player1_class = __import__(str(folder_player+p1.name+"_tictac"), fromlist=[None])
        player2_class = __import__(str(folder_player+p2.name+"_tictac"), fromlist=[None])
        return LocalPlayerProxy(player1_class.MyPlayer("X", name="louis")), LocalPlayerProxy(player2_class.MyPlayer("O", name="loic"))
