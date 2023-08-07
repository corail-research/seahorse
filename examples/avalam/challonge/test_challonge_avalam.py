import asyncio

import nest_asyncio

from seahorse.tournament.challonge_tournament import ChallongeTournament


async def fonction() :
    t = ChallongeTournament(id_challonge="Seahorse_Corail", keypass_challonge="WG8g6kBT5AYvaonSi7Ae0pWeKFZgXaHXMZhIDOR6", game_name="challonge_avalam", log_level="INFO")
    await t.create_tournament(tournament_name="challonge_avalam",tournament_url="seahorse_test_avalam",csv_file="players_avalam.csv")
    #await t.connect_tournament(tournament_name="challonge_avalam")
    await t.run(folder_player="seahorse.examples.avalam.",rounds=3,nb_process=4)

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(fonction())
