import csv
from abc import abstractmethod

import challonge

from coliseum.utils.custom_exceptions import ConnectionProblemError, MethodNotImplementedError, NoTournamentFailError


class ChallongeTournament:
    def __init__(self, id_challonge, keypass_challonge, folder_player, log_file=None) -> None:
        self.user = None
        self.id_challonge = id_challonge
        self.keypass_challonge = keypass_challonge
        self.folder_player = folder_player
        self.log_file = log_file
        self.tournament = None

    @abstractmethod
    def build_initial_rep(self):
        raise MethodNotImplementedError()

    @abstractmethod
    def build_initial_scores(self, p1, p2):
        raise MethodNotImplementedError()

    @abstractmethod
    def build_initial_game_state(self, p1, p2, scores, rep):
        raise MethodNotImplementedError()

    @abstractmethod
    def build_initial_master(self, p1, p2, game_state):
        raise MethodNotImplementedError()

    @abstractmethod
    def build_players(self, p1, p2, folder_player) :
        raise MethodNotImplementedError()

    async def connect_tournament(self, tournament_name) :
        self.user = await challonge.get_user(self.id_challonge, self.keypass_challonge)
        my_tournaments = await self.user.get_tournaments()
        for t in my_tournaments:
            if t.name == tournament_name :
                self.tournament = t
                return
        raise ConnectionProblemError()

    async def create_tournament(self, tournament_name, tournament_url, csv_file, sep=",") :
        self.user = await challonge.get_user(self.id_challonge, self.keypass_challonge)
        self.tournament = await self.user.create_tournament(name=tournament_name, url=tournament_url)
        with open(csv_file) as csvfile :
            spamreader = csv.reader(csvfile, delimiter=sep)
            for line in spamreader :
                for name in line :
                    await self.tournament.add_participant(str(name))

    def format_scores(self, scores, player_1) :
        sub_str_1 = None
        sub_str_2 = None
        for key in scores.keys() :
            if key == player_1.get_id() :
                sub_str_1 = str(int(scores[key]))
            else :
                sub_str_2 = str(int(scores[key]))
        return sub_str_1 + "-" + sub_str_2

    def format_winner(self, winner, player_1, p1, p2) :
        if winner.get_id() == player_1.get_id() :
            return p1
        else :
            return p2

    async def run(self,rounds=1) :
        if self.tournament is not None :
            await self.tournament.start()
            matches = await self.tournament.get_matches()
            for match in matches :
                scores = ""
                winners = []
                for r in range(rounds) :
                    p1 = await self.tournament.get_participant(match.player1_id)
                    p2 = await self.tournament.get_participant(match.player2_id)
                    player_1, player_2 = self.build_players(p1, p2, self.folder_player)
                    init_rep = self.build_initial_rep()
                    if r % 2 == 0 :
                        init_scores = self.build_initial_scores(player_1,player_2)
                        init_game_state = self.build_initial_game_state(player_1, player_2, init_scores, init_rep)
                        master = self.build_initial_master(player_1,player_2,init_game_state)
                    else :
                        init_scores = self.build_initial_scores(player_2,player_1)
                        init_game_state = self.build_initial_game_state(player_2, player_1, init_scores, init_rep)
                        master = self.build_initial_master(player_2,player_1,init_game_state)
                    master.record_game()
                    scores += self.format_scores(master.get_scores(), player_1) + ","
                    winners.append(self.format_winner(master.get_winner()[0], player_1, p1, p2))
                await match.report_winner(max(winners,key=winners.count),scores[:-1])
            await self.tournament.finalize()
        else :
            raise NoTournamentFailError()
