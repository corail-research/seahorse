import asyncio
import time

import nest_asyncio

from seahorse.tournament.challonge_tournament import ChallongeTournament


async def fonction() :
    t = ChallongeTournament(id_challonge="Seahorse_Corail", keypass_challonge="WG8g6kBT5AYvaonSi7Ae0pWeKFZgXaHXMZhIDOR6", game_name="main_tictac", log_level="INFO")
    await t.create_tournament(tournament_name="challonge_tictac_s5",tournament_url="seahorse_test_tictac_"+str(int(time.time()*1000)),csv_file="players_tictac.csv")
    #await t.connect_tournament(tournament_name="challonge_tictac_s5")
    await t.run(folder_player="",rounds=3,nb_process=4, minormax="max")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(fonction())
