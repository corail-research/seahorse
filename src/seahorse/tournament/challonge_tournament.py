from __future__ import annotations

import asyncio
import csv
import math
from sys import platform

import challonge
from split import chop

from seahorse.utils.custom_exceptions import ConnectionProblemError, NoTournamentFailError


class ChallongeTournament:
    """
    A class to interact with the Challonge tournament platform.

    Attributes:
        id_challonge (str): The Challonge ID.
        keypass_challonge (str): The Challonge API key.
        game_name (str): The name of the game.
        log_level (str): The log file.
    """

    def __init__(self, id_challonge: str, keypass_challonge: str, game_name: str, log_level: str|None, log_file: str = "log.txt") -> None:
        """
        Initializes a new instance of the ChallongeTournament class.

        Args:
            id_challonge (str): The Challonge ID.
            keypass_challonge (str): The Challonge API key.
            game_name (str): The name of the game.
            log_level (str): The log file. Default is None.
        """
        self.id_challonge = id_challonge
        self.keypass_challonge = keypass_challonge
        self.game_name = game_name
        self.log_level = log_level
        self.user = None
        self.tournament = None
        self.log_file = log_file
        self.created = False

    async def create_tournament(self, tournament_name: str, tournament_url: str, csv_file: str, sep: str = ",") -> None:
        """
        Creates a new tournament on Challonge and adds participants from a CSV file.

        Args:
            tournament_name (str): The name of the tournament.
            tournament_url (str): The URL of the tournament.
            csv_file (str): The path to the CSV file containing participant names.
            sep (str): The delimiter used in the CSV file. Default is ",".

        Returns:
            None
        """
        self.user = await challonge.get_user(self.id_challonge, self.keypass_challonge)
        self.tournament = await self.user.create_tournament(name=tournament_name, url=tournament_url)
        with open(csv_file) as csvfile :
            spamreader = csv.reader(csvfile, delimiter=sep)
            for line in spamreader :
                for name in line :
                    await self.tournament.add_participant(str(name))
        self.created = True

    async def connect_tournament(self, tournament_name: str) -> None:
        """
        Connects to an existing tournament on Challonge.

        Args:
            tournament_name (str): The name of the tournament.

        Returns:
            None

        Raises:
            ConnectionProblemError: If the connection to the tournament fails.
        """
        self.user = await challonge.get_user(self.id_challonge, self.keypass_challonge)
        my_tournaments = await self.user.get_tournaments()
        for t in my_tournaments:
            if t.name == tournament_name :
                self.tournament = t
                return
        raise ConnectionProblemError()

    def retrieve_scores(self, match) -> str:
        """
        Retrieves the scores from a match.

        Args:
            match: The match object.

        Returns:
            str: The scores as a string.
        """
        if not match.scores_csv :
            return match.scores_csv
        return match.scores_csv + ","

    def retrieve_winners(self, scores: str, p1, p2, minormax: str) -> list :
        """
        Retrieves the winners from the scores.

        Args:
            scores (str): The scores as a string.
            p1: The participant object of player 1.
            p2: The participant object of player 2.

        Returns:
            list: A list of winners.
        """
        result = []
        if not scores :
            return result
        list_scores = scores[:-1].split(",")
        for score in list_scores:
            s1, s2 = score.split("-")
            if minormax == "max" :
                if s1 > s2 :
                    result.append(p1)
                elif s1 < s2 :
                    result.append(p2)
            elif minormax == "min" :
                if s1 > s2 :
                    result.append(p2)
                elif s1 < s2 :
                    result.append(p1)
        return result

    def invert_score(self, score: str) -> str:
        """
        Inverts the score.

        Args:
            score (str): The score as a string.

        Returns:
            str: The inverted score.
        """
        list_score = score[:-1].split("-")
        return list_score[1] + "-" + list_score[0] + ","

    def get_participant_winner(self, winner: str, p1, p2):
        """
        Gets the participant object of the winner.

        Args:
            winner (str): The name of the winner.
            p1: The participant object of player 1.
            p2: The participant object of player 2.

        Returns:
            The participant object of the winner.
        """
        if winner == p1.name :
            return p1
        else :
            return p2

    async def play_round(self,name1: str, name2: str, port: int, folder_player: str) -> tuple[str, str]:
        """
        Plays a round of the tournament.

        Args:
            name1 (str): The name of player 1.
            name2 (str): The name of player 2.
            port (int): The port number.
            folder_player (str): The folder containing the player scripts.

        Returns:
            tuple[str, str]: A tuple containing the score and the winner.
        """
        if platform == "win32" :
            cmd = "python " + self.game_name + ".py" + " -t local -p " + str(port) + " " + folder_player+name1 + " " + folder_player+name2
        else :
            cmd = "python3 " + self.game_name + ".py" + " -t local -p " + str(port) + " " + name1 + " " + name2
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        score1 = stderr.decode("utf-8").split("\n")[-4].split(" - ")[-1]
        score2 = stderr.decode("utf-8").split("\n")[-3].split(" - ")[-1]
        winner = stderr.decode("utf-8").split("\n")[-2].split(" - ")[-1]
        score = str(math.floor(abs(float(score1)))) + "-" + str(math.floor(abs(float(score2)))) + ","
        winner = str(winner)
        with open(self.log_file,"a+") as f :
            f.write(stderr.decode(encoding="utf-8"))
        f.close()
        return score, winner

    async def play_match(self, match, port: int, rounds: int, folder_player: str, minormax: str) -> None:
        """
        Plays a match of the tournament.

        Args:
            match: The match object.
            port (int): The port number.
            rounds (int): The number of rounds.
            folder_player (str): The folder containing the player scripts.

        Returns:
            None
        """
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
                winners = self.retrieve_winners(scores, p1, p2, minormax)
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
            if match.group_id is not None :
                await match._report(scores[:-1], max(winners,key=winners.count).group_player_ids[0])
            else :
                await match._report(scores[:-1], max(winners,key=winners.count).id)
            await match.unmark_as_underway()

    async def run(self, folder_player: str, rounds: int = 1, nb_process: int = 2, minormax: str = "max") -> None:
        """
        Runs the tournament.

        Args:
            folder_player (str): The folder containing the player scripts.
            rounds (int): The number of rounds. Default is 1.
            nb_process (int): The number of parallel processes. Default is 2.

        Returns:
            None

        Raises:
            NoTournamentFailError: If there is no tournament.
        """
        if self.tournament is not None :
            if self.created :
                await self.tournament.start()
            matches = await self.tournament.get_matches()
            dict_round = {}
            for match in matches :
                if match.group_id is None :
                    if dict_round.get(match.round,False) :
                        dict_round[match.round] += [match]
                    else :
                        dict_round[match.round] = [match]
                elif dict_round.get(match.group_id,False) :
                    dict_round[match.group_id] += [match]
                else :
                    dict_round[match.group_id] = [match]
            for key in dict_round.keys() :
                port = 16000
                for matches in list(chop(nb_process, dict_round[key])) :
                    list_jobs_routines = [asyncio.create_task(self.play_match(match, port+i, rounds, folder_player, minormax)) for i, match in enumerate(matches)]
                    await asyncio.gather(*list_jobs_routines)
            if self.created :
                await self.tournament.finalize()
        else :
            raise NoTournamentFailError()
