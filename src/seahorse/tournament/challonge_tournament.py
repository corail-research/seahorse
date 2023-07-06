from __future__ import annotations

import asyncio
import csv
import math
from sys import platform

import challonge
from split import chop

from seahorse.utils.custom_exceptions import ConnectionProblemError, NoTournamentFailError


class ChallongeTournament:
    def __init__(self, id_challonge: str, keypass_challonge: str, game_name: str, log_file: str = None) -> None:
        self.id_challonge = id_challonge
        self.keypass_challonge = keypass_challonge
        self.game_name = game_name
        self.log_file = log_file
        self.user = None
        self.tournament = None

    async def create_tournament(self, tournament_name: str, tournament_url: str, csv_file: str, sep: str = ",") -> None:
        self.user = await challonge.get_user(self.id_challonge, self.keypass_challonge)
        self.tournament = await self.user.create_tournament(name=tournament_name, url=tournament_url)
        with open(csv_file) as csvfile :
            spamreader = csv.reader(csvfile, delimiter=sep)
            for line in spamreader :
                for name in line :
                    await self.tournament.add_participant(str(name))

    async def connect_tournament(self, tournament_name: str) -> None:
        self.user = await challonge.get_user(self.id_challonge, self.keypass_challonge)
        my_tournaments = await self.user.get_tournaments()
        for t in my_tournaments:
            if t.name == tournament_name :
                self.tournament = t
                return
        raise ConnectionProblemError()

    def retrieve_scores(self, match) -> str:
        if not match.scores_csv :
            return match.scores_csv
        return match.scores_csv + ","

    def retrieve_winners(self, scores: str, p1, p2) -> list :
        result = []
        if not scores :
            return result
        list_scores = scores[:-1].split(",")
        for score in list_scores:
            s1, s2 = score.split("-")
            if s1 >= s2 :
                result.append(p1)
            else :
                result.append(p2)
        return result

    def invert_score(self, score: str) -> str:
        list_score = score[:-1].split("-")
        return list_score[1] + "-" + list_score[0] + ","

    def get_participant_winner(self, winner: str, p1, p2):
        if winner == p1.name :
            return p1
        else :
            return p2

    async def play_round(self,name1: str, name2: str, port: int, folder_player: str) -> tuple[str, str]:
        if platform == "win32" :
            cmd = "py " + self.game_name + ".py" + " " + folder_player + " " + name1 + " " + name2 + " " + str(port)
        else :
            cmd = "python3 " + self.game_name + ".py" + " " + folder_player + " " + name1 + " " + name2 + " " + str(port)
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        list_score_winner = stdout.decode("utf-8").split("\n")[-2].split(",")
        score = str(math.floor(float(list_score_winner[0]))) + "-" + str(math.floor(float(list_score_winner[1]))) + ","
        winner = str(list_score_winner[2])
        return score, winner

    async def play_match(self, match, port: int, rounds: int, folder_player: str) -> None:
        if match.completed_at is None :
            p1 = await self.tournament.get_participant(match.player1_id)
            p2 = await self.tournament.get_participant(match.player2_id)
            already_played = 0
            if match.underway_at is None :
                await match.mark_as_underway()
                scores = ""
                winners = []
            else :
                scores = self.retrieve_scores(match)
                winners = self.retrieve_winners(scores, p1, p2)
                already_played = len(winners)
            for r in range(already_played, rounds) :
                if r % 2 == 0 :
                    score, winner = await self.play_round(p1.name, p2.name, port, folder_player)
                    scores += score
                    winners.append(self.get_participant_winner(winner, p1, p2))
                else :
                    score, winner = await self.play_round(p2.name, p1.name, port, folder_player)
                    scores += self.invert_score(score)
                    winners.append(self.get_participant_winner(winner, p1, p2))
                await match.report_live_scores(scores[:-1])
            await match.report_winner(max(winners,key=winners.count),scores[:-1])
            await match.unmark_as_underway()

    async def run(self, folder_player: str, rounds: int = 1, nb_process: int = 2) -> None:
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
                port = 16000
                for matches in list(chop(nb_process, dict_round[key])) :
                    list_jobs_routines = [asyncio.create_task(self.play_match(match, port+i, rounds, folder_player)) for i, match in enumerate(matches)]
                    await asyncio.gather(*list_jobs_routines)
            await self.tournament.finalize()
        else :
            raise NoTournamentFailError()
