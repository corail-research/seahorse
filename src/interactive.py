import asyncio
import copy
import time
from typing import Type

from seahorse.examples.tictactoe.alpha_player_tictac import MyPlayer as AlphaPlayerTictac
from seahorse.examples.tictactoe.game_state_tictac import GameStateTictac
from seahorse.examples.tictactoe.player_tictac import PlayerTictac
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.player.proxies import LocalPlayerProxy


class InteractivePlayer(PlayerTictac):
    def __init__(self, piece_type: str, name: str = "bob", **kwargs) -> None:
        super().__init__(piece_type, name, **kwargs)

    async def blabla(self) :
        print("wouhou")
        asyncio.ensure_future(asyncio.create_task(time.sleep(100)))

    def compute_action(self, current_state: GameState, **kargs) -> Action:
        print("Current state:")
        print(current_state.get_rep())
        id = int(input("Select an action (int):"))
        return list(current_state.get_possible_actions())[id]

player1 = LocalPlayerProxy(InteractivePlayer("O", name="jean"),masterless=True,gs=GameStateTictac)
asyncio.new_event_loop().run_until_complete(player1.listen(keep_alive=True,master_address="http://localhost:16001"))
