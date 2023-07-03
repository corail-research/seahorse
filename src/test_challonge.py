import asyncio

import nest_asyncio

from seahorse.examples.tictactoe.challonge_tournament_tictac import ChallongeTournamentTictac


async def fonction() :
    t = ChallongeTournamentTictac(id_challonge="Seahorse_Corail", keypass_challonge="WG8g6kBT5AYvaonSi7Ae0pWeKFZgXaHXMZhIDOR6", folder_player="seahorse.examples.tictactoe.", log_file="log.txt")
    #await t.create_tournament(tournament_name="test_1",tournament_url="seahorse_test_5",csv_file="players.csv")
    #await t.connect_tournament(tournament_name="test_1")
    await t.run(rounds=3,tournament_name="test",tournament_url="seahorse_tournament_2",exist=False,csv_file="players.csv")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(fonction())
