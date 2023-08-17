import asyncio
import csv
from sys import platform

from split import chop


class ExecMulti:
    """
    A class to execute multiple rounds and matches of a game.

    Attributes:
        main_file (str): The main file to execute.
        num_player (int): The number of players in each match.
    """

    def __init__(self, main_file: str, log_file: str = "log.txt") -> None:
        """
        Initializes a new instance of the ExecMulti class.

        Args:
            main_file (str): The main file to execute.
        """
        self.main_file = main_file
        self.num_player = 2
        self.log_file = log_file

    async def run_round(self, folder_players: str, name_player1: str, name_player2: str, port: int, recordjs: bool):
        """
        Runs a single round of the game.

        Args:
            folder_players (str): The folder containing the player files.
            name_player1 (str): The name of player 1.
            name_player2 (str): The name of player 2.
            port (int): The port number for communication.

        Returns:
            None
        """
        if platform == "win32" :
            cmd = "python " + self.main_file + ".py" + " -t local"
            if recordjs :
                cmd += " --record"
            cmd += " -p " + str(port) + " " + folder_players+name_player1 + " " + folder_players+name_player2
        else :
            cmd = "python3 " + self.main_file + ".py" + " -t local"
            if recordjs :
                cmd += " --record"
            cmd += " -p " + str(port) + " " + folder_players+name_player1 + " " + folder_players+name_player2
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        with open(self.log_file,"a+") as f :
            f.write(stderr.decode(encoding="utf-8"))
        f.close()

    async def run_multiple_rounds(self, rounds: int, nb_process: int, swap: bool, folder_players: str, name_player1: str, name_player2: str, port: int = 8080, *, recordjs: bool = False):
        """
        Runs multiple rounds of the game.

        Args:
            rounds (int): The number of rounds to run.
            nb_process (int): The number of processes to use.
            swap (bool): Whether to swap the players in alternate rounds.
            folder_players (str): The folder containing the player files.
            name_player1 (str): The name of player 1.
            name_player2 (str): The name of player 2.
            port (int): The port number for communication. Default is 8080.

        Returns:
            None
        """
        for chunk in list(chop(nb_process, range(rounds))):
            list_jobs_routines = []
            for add, _ in enumerate(chunk):
                if swap:
                    if add % 2 == 0:
                        p1 = name_player1
                        p2 = name_player2
                    else:
                        p1 = name_player2
                        p2 = name_player1
                else:
                    p1 = name_player1
                    p2 = name_player2
                list_jobs_routines.append(asyncio.create_task(self.run_round(folder_players, p1, p2, port+add, recordjs)))
            await asyncio.gather(*list_jobs_routines)

    async def run_match(self, rounds_by_match: int, swap: bool, folder_players: str, name_player1: str, name_player2: str, port: int, recordjs: bool):
        """
        Runs a single match of the game.

        Args:
            rounds_by_match (int): The number of rounds per match.
            swap (bool): Whether to swap the players in alternate matches.
            folder_players (str): The folder containing the player files.
            name_player1 (str): The name of player 1.
            name_player2 (str): The name of player 2.
            port (int): The port number for communication.

        Returns:
            None
        """
        await self.run_multiple_rounds(rounds=rounds_by_match, nb_process=1, swap=swap, folder_players=folder_players, name_player1=name_player1, name_player2=name_player2, port=port, recordjs=recordjs)

    async def run_multiple_matches(self, rounds_by_match: int, nb_process: int, swap: bool, folder_players: str, csv_file: str, sep: str = ",", port: int = 8080, *, recordjs: bool = False):
        """
        Runs multiple matches of the game.

        Args:
            rounds_by_match (int): The number of rounds per match.
            nb_process (int): The number of processes to use.
            swap (bool): Whether to swap the players in alternate matches.
            folder_players (str): The folder containing the player files.
            csv_file (str): The CSV file containing the names of the players.
            sep (str): The delimiter used in the CSV file. Default is ",".
            port (int): The starting port number for communication. Default is 8080.

        Returns:
            None
        """
        with open(csv_file) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=sep)
            match_table = []
            for line in spamreader:
                counter = 0
                match = []
                for name in line:
                    match.append(name)
                    if len(match) == self.num_player:
                        match_table.append(match)
                        match = []
                        counter = 0
                    else:
                        counter += 1
            for chunk in list(chop(nb_process, match_table)):
                list_jobs_routines = []
                for add, match in enumerate(chunk):
                    list_jobs_routines.append(asyncio.create_task(self.run_match(rounds_by_match, swap, folder_players, match[0], match[1], port+add, recordjs)))
                await asyncio.gather(*list_jobs_routines)
