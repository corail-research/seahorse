import asyncio

from game_state_avalam import GameStateAvalam
from random_player_avalam import MyPlayer as RandomPlayerTictac
from seahorse.player.proxies import LocalPlayerProxy

player1 = LocalPlayerProxy(RandomPlayerTictac(piece_type="R",name="bob"),masterless=True,gs=GameStateAvalam)
asyncio.new_event_loop().run_until_complete(player1.listen(keep_alive=True,master_address="http://localhost:16001"))
