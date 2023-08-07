import asyncio

from game_state_abalone import GameStateAbalone
from random_player_abalone import MyPlayer as RandomPlayerAbalone
from seahorse.player.proxies import LocalPlayerProxy

player1 = LocalPlayerProxy(RandomPlayerAbalone(piece_type="W", name= "marcel"),gs=GameStateAbalone)
asyncio.new_event_loop().run_until_complete(player1.listen(keep_alive=True,master_address="http://10.200.37.65:16001"))
