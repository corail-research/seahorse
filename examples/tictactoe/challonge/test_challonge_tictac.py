import asyncio

import nest_asyncio

from seahorse.tournament.challonge_tournament import ChallongeTournament


async def fonction() :
    t = ChallongeTournament(id_challonge="logru", keypass_challonge="3UDnkNKWWMGUVKD54GNIupeoFrJijLlkfMMy8l0y", game_name="challonge_tictac", log_file="log.txt")
    await t.create_tournament(tournament_name="challonge_tictac",tournament_url="seahorse_test_tictac_customxdxafdxdfs",csv_file="players_tictac.csv")
    #await t.connect_tournament(tournament_name="challonge_tictac")
    await t.run(folder_player="seahorse.examples.tictactoe.",rounds=3,nb_process=4)

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(fonction())
