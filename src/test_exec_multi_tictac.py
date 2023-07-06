import asyncio

import nest_asyncio

from seahorse.execution.exec_multi import ExecMulti

if __name__ == "__main__":
    nest_asyncio.apply()
    e = ExecMulti(main_file="challonge_tictac")
    asyncio.run(e.run_multiple_rounds(rounds=40, nb_process=40, swap=True, folder_players="seahorse.examples.tictactoe.", name_player1="random_player_tictac", name_player2="random_player_2_tictac", port=8080))
    #asyncio.run(e.run_multiple_matches(rounds_by_match=6, nb_process=8, swap=True, folder_players="seahorse.examples.tictactoe.", csv_file="players.csv", sep=","))
