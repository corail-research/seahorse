import asyncio
import csv
from sys import platform

from split import chop


class ExecMulti() :
    def __init__(self, main_file: str) -> None:
        self.main_file = main_file
        self.num_player = 2

    async def run_round(self, folder_players: str, name_player1: str, name_player2: str, port: int):
        if platform == "win32" :
            cmd = "py " + self.main_file + ".py" + " " + folder_players + " " + name_player1 + " " + name_player2 + " " + str(port)
        else :
            cmd = "python3 " + self.main_file + ".py" + " " + folder_players + " " + name_player1 + " " + name_player2 + " " + str(port)
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await process.communicate()
        #list_score_winner = stdout.decode("utf-8").split("\n")[-2].split(",")
        #score = str(math.floor(float(list_score_winner[0]))) + "-" + str(math.floor(float(list_score_winner[1]))) + ","
        #winner = str(list_score_winner[2])

    async def run_multiple_rounds(self, rounds: int, nb_process: int, swap: bool, folder_players: str, name_player1: str, name_player2: str, port: int = 8080) :
        for chunk in list(chop(nb_process, range(rounds))) :
            list_jobs_routines = []
            for add, _ in enumerate(chunk) :
                if swap :
                    if add % 2 == 0 :
                        p1 = name_player1
                        p2 = name_player2
                    else :
                        p1 = name_player2
                        p2 = name_player1
                else :
                    p1 = name_player1
                    p2 = name_player2
                list_jobs_routines.append(asyncio.create_task(self.run_round(folder_players, p1, p2, port+add)))
            await asyncio.gather(*list_jobs_routines)

    async def run_match(self, rounds_by_match: int, swap: bool, folder_players: str, name_player1: str, name_player2: str, port: int) :
        await self.run_multiple_rounds(rounds=rounds_by_match, nb_process=1, swap=swap, folder_players=folder_players, name_player1=name_player1, name_player2=name_player2, port=port)

    async def run_multiple_matches(self, rounds_by_match: int, nb_process: int, swap: bool, folder_players: str, csv_file: str, sep: str = ",", port: int = 8080) :
        with open(csv_file) as csvfile :
            spamreader = csv.reader(csvfile, delimiter=sep)
            match_table = []
            for line in spamreader :
                counter = 0
                match = []
                for name in line :
                    match.append(name)
                    if len(match) == self.num_player :
                        match_table.append(match)
                        match = []
                        counter = 0
                    else :
                        counter += 1
            for chunk in list(chop(nb_process, match_table)) :
                list_jobs_routines = []
                for add, match in enumerate(chunk) :
                    list_jobs_routines.append(asyncio.create_task(self.run_match(rounds_by_match, swap, folder_players, match[0], match[1], port+add)))
                await asyncio.gather(*list_jobs_routines)
