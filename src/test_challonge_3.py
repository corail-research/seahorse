import asyncio

import nest_asyncio

from seahorse.tournament.challonge_tournament_3 import ChallongeTournament


async def fonction() :
    t = ChallongeTournament(id_challonge="Seahorse_Corail", keypass_challonge="WG8g6kBT5AYvaonSi7Ae0pWeKFZgXaHXMZhIDOR6", game_name="challonge_3", log_file="log.txt")
    await t.create_tournament(tournament_name="test_1",tournament_url="seahorse_test_912234433434555556455",csv_file="players.csv")
    #await t.connect_tournament(tournament_name="test_1")
    await t.run(folder_player="seahorse.examples.tictactoe.",rounds=3,nb_process=4)

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(fonction())
