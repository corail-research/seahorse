from __future__ import annotations

import asyncio
import csv
from abc import abstractmethod

import challonge

from seahorse.utils.custom_exceptions import ConnectionProblemError, MethodNotImplementedError, NoTournamentFailError


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

    def retrieve_scores(self, match) :
        return match.scores_csv + ","

    def retrieve_winners(self, scores, p1, p2) :
        result = []
        list_scores = scores[:-1].split(",")
        for score in list_scores:
            s1, s2 = score.split("-")
            if s1 >= s2 :
                result.append(p1)
            else :
                result.append(p2)
        return result

    async def play_match(self, match, rounds) :
        if match.completed_at is None :
            #print(match.round)
            p1 = await self.tournament.get_participant(match.player1_id)
            p2 = await self.tournament.get_participant(match.player2_id)
            player_1, player_2 = self.build_players(p1, p2, self.folder_player)
            already_played = 0
            if match.underway_at is None :
                await match.mark_as_underway()
                scores = ""
                winners = []
            else :
                scores = self.retrieve_scores(match)
                winners = self.retrieve_winners(scores, p1, p2)
                already_played = len(winners)
            #print("=========NEW MATCH=========")
            for r in range(already_played, rounds) :
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
                #print(match.player1_id, match.player2_id, self.format_scores(master.get_scores(), player_1))
                scores += self.format_scores(master.get_scores(), player_1) + ","
                await match.report_live_scores(scores[:-1])
                winners.append(self.format_winner(master.get_winner()[0], player_1, p1, p2))
            await match.report_winner(max(winners,key=winners.count),scores[:-1])
            await match.unmark_as_underway()

    # async def run(self, rounds=1):
    #     if self.tournament is not None :
    #         await self.tournament.start()
    #         matches = await self.tournament.get_matches()
    #         for match in matches:
    #             await self.play_match(match,rounds)
    #         await self.tournament.finalize()
    #     else :
    #         raise NoTournamentFailError()

    async def run(self,rounds=1) :
        max_thread = 2
        if self.tournament is not None :
            await self.tournament.start()
            matches = await self.tournament.get_matches()
            dict_round = {}
            for match in matches :
                if dict_round.get(match.round,False) :
                    dict_round[match.round] += [match]
                else :
                    dict_round[match.round] = [match]
            for key in sorted(dict_round.keys()) :
                counter = 0
                list_jobs = []
                while dict_round[key] :
                    if counter < max_thread :
                        list_jobs.append(asyncio.create_task(self.play_match(dict_round[key].pop(),rounds)))
                    else :
                        await asyncio.gather(*list_jobs)
                        list_jobs = []
                if list_jobs :
                    await asyncio.gather(*list_jobs)
            await self.tournament.finalize()
        else :
            raise NoTournamentFailError()

    # async def loop_matches(self, matches, rounds) :
    #     for match in matches :
    #         print(match)
    #         await self.play_match(match,rounds)

    # def async_wrapper(self, matches, rounds):
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     result = loop.run_until_complete(self.loop_matches(matches, rounds))
    #     loop.close()
    #     return result

    # async def async_task(self, matches, rounds) :
    #     print(matches)
    #     loop = asyncio.get_event_loop()
    #     print(matches)
    #     await loop.run_in_executor(None,self.async_wrapper, matches, rounds)

    # async def run(self, rounds=1) :
    #     loop = asyncio.get_event_loop()
    #     max_threads = 2
    #     if self.tournament is not None :
    #         await self.tournament.start()
    #         matches = await self.tournament.get_matches()
    #         dict_round = {}
    #         for match in matches :
    #             if dict_round.get(match.round,False) :
    #                 dict_round[match.round] += [match]
    #             else :
    #                 dict_round[match.round] = [match]
    #         for key in sorted(dict_round.keys()) :
    #             #print(key)
    #             tasks = []
    #             for batch in list(chop(math.ceil(len(dict_round[key])/max_threads), dict_round[key])):
    #                 #print(batch)
    #                 tasks.append(asyncio.create_task(self.async_task(batch,rounds)))
    #             loop.run_until_complete(asyncio.gather(*tasks))
    #         await self.tournament.finalize()
    #         loop.close()
    #     else :
    #         raise NoTournamentFailError()

