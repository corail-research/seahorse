import asyncio
from seahorse.examples.tictactoe.alpha_player_tictac import MyPlayer as AlphaPlayerTictac
from seahorse.examples.tictactoe.game_state_tictac import GameStateTictac
from seahorse.player.proxies import LocalPlayerProxy


player1 = LocalPlayerProxy(AlphaPlayerTictac("O", name="jean"),masterless=True,gs=GameStateTictac)
asyncio.new_event_loop().run_until_complete(player1.listen(keep_alive=True))
