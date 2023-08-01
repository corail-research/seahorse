import json
from seahorse.examples.tictactoe.alpha_player_tictac import MyPlayer as AlphaPlayerTictac
from seahorse.examples.tictactoe.board_tictac import BoardTictac
from seahorse.examples.tictactoe.game_state_tictac import GameStateTictac
from seahorse.examples.tictactoe.master_tictac import MasterTictac
from seahorse.examples.tictactoe.player_tictac import PlayerTictac
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster
from seahorse.player.player import Player
from seahorse.player.proxies import LocalPlayerProxy, RemotePlayerProxy


class InteractivePlayerProxy(LocalPlayerProxy):
    def __init__(self, mimics: type[Player], *args, **kwargs) -> None:
        super().__init__(mimics, *args, **kwargs)
        self.wrapped_player.player_type = "interactive"

    async def play(self, current_state: GameState) -> Action:
        while True:
            data = json.loads(await EventMaster.get_instance().wait_for_event("interact"))
            action = current_state.convert_light_action_to_action(data)
            if action in current_state.get_possible_actions():
                break
            else:
                await EventMaster.get_instance().sio.emit("ActionNotPermitted",None)
        return action

def run_multiple_games():
    for _ in range(1):
        player1 = LocalPlayerProxy(AlphaPlayerTictac("X", name="louis"),gs=GameStateTictac)
        player2 = InteractivePlayerProxy(PlayerTictac("O", name="pierre"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        init_rep = BoardTictac(env={}, dim=[3, 3])
        initial_game_state = GameStateTictac(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep)

        master = MasterTictac(
            name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_file="log.txt", port=16001
        )
        master.record_game()

run_multiple_games()
