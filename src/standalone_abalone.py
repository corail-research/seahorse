import asyncio

from seahorse.examples.abalone.game_state_abalone import GameStateAbalone
from seahorse.examples.abalone.random_player_abalone import MyPlayer as RandomPlayerAbalone
from seahorse.player.proxies import LocalPlayerProxy

player1 = LocalPlayerProxy(RandomPlayerAbalone(piece_type="W", name= "bob"),masterless=True,gs=GameStateAbalone)
asyncio.new_event_loop().run_until_complete(player1.listen(keep_alive=True,master_address="http://localhost:16001"))
