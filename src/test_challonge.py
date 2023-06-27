import asyncio

import nest_asyncio
from coliseum.examples.tictactoe.challonge_tournament_tictac import ChallongeTournamentTictac

nest_asyncio.apply()

async def fonction() :
    t = ChallongeTournamentTictac(id_challonge="Seahorse_Corail", keypass_challonge="WG8g6kBT5AYvaonSi7Ae0pWeKFZgXaHXMZhIDOR6", folder_player="coliseum.examples.tictactoe.", log_file="log.txt")
    await t.create_tournament(tournament_name="test",tournament_url="seahorse_test",csv_file="players.csv")
    #await t.connect_tournament(tournament_name="test")
    await t.run(rounds=5)

asyncio.run(fonction())
