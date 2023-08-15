import asyncio

import nest_asyncio

from seahorse.execution.exec_multi import ExecMulti

if __name__ == "__main__":
    nest_asyncio.apply()
    e = ExecMulti(main_file="main_tictac", log_file="log.txt")
    asyncio.run(e.run_multiple_rounds(rounds=5, nb_process=5, swap=True, folder_players=".", name_player1="random_player_tictac", name_player2="alpha_player_tictac", port=8080))
    #asyncio.run(e.run_multiple_matches(rounds_by_match=6, nb_process=8, swap=True, folder_players=".", csv_file="players.csv", sep=","))
