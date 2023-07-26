import json
from seahorse.examples.abalone.alpha_player_abalone import MyPlayer as AlphaPlayerAbalone
from seahorse.examples.abalone.board_abalone import BoardAbalone
from seahorse.examples.abalone.game_state_abalone import GameStateAbalone
from seahorse.examples.abalone.master_abalone import MasterAbalone
from seahorse.examples.abalone.player_abalone import PlayerAbalone
from seahorse.examples.abalone.random_player_abalone import MyPlayer as RandomPlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.game.io_stream import EventMaster, remote_action
from seahorse.player.player import Player
from seahorse.player.proxies import LocalPlayerProxy, RemotePlayerProxy
from aiohttp import web

W = 1
B = 2

class InteractivePlayerProxy(LocalPlayerProxy):
    def __init__(self, mimics: type[Player], *args, **kwargs) -> None:
        super().__init__(mimics, *args, **kwargs)

    async def play(self, current_state: GameState) -> Action:
        #print("xxxxx")
        data = json.loads(await EventMaster.get_instance().wait_for_event("interact"))
        
        
        #print("++++++")
        return current_state.convert_light_action_to_action(data["from"], data["to"])

def run_multiple_games():
    for _ in range(1):
        
        player1 = LocalPlayerProxy(AlphaPlayerAbalone(piece_type="B"))
        player2 = InteractivePlayerProxy(PlayerAbalone(piece_type="W", name="nani"))

        list_players = [player1, player2]
        init_scores = {player1.get_id(): 0, player2.get_id(): 0}
        print("init_scores", init_scores)
        dim = [17, 9]
        env = {}
        # 0 case non accessible
        # 1 case player 1
        # 2 case player 2
        # 3 case vide accessible
        # CLASSIQUE
        # initial_board = [
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        #     [0, 0, 0, 1, 0, 1, 0, 0, 0],
        #     [0, 0, 1, 0, 1, 0, 3, 0, 0],
        #     [0, 1, 0, 1, 0, 3, 0, 3, 0],
        #     [1, 0, 1, 0, 1, 0, 3, 0, 3],
        #     [0, 1, 0, 1, 0, 3, 0, 3, 0],
        #     [1, 0, 1, 0, 3, 0, 3, 0, 3],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [3, 0, 3, 0, 3, 0, 3, 0, 3],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [3, 0, 3, 0, 3, 0, 2, 0, 2],
        #     [0, 3, 0, 3, 0, 2, 0, 2, 0],
        #     [3, 0, 3, 0, 2, 0, 2, 0, 2],
        #     [0, 3, 0, 3, 0, 2, 0, 2, 0],
        #     [0, 0, 3, 0, 2, 0, 2, 0, 0],
        #     [0, 0, 0, 2, 0, 2, 0, 0, 0],
        #     [0, 0, 0, 0, 2, 0, 0, 0, 0],
        # ]
        # MARGUERITE
        # initial_board = [
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        #     [0, 0, 0, 1, 0, 1, 0, 0, 0],
        #     [0, 0, 3, 0, 1, 0, 3, 0, 0],
        #     [0, 2, 0, 1, 0, 1, 0, 3, 0],
        #     [2, 0, 2, 0, 1, 0, 3, 0, 3],
        #     [0, 2, 0, 3, 0, 3, 0, 3, 0],
        #     [2, 0, 2, 0, 3, 0, 3, 0, 3],
        #     [0, 2, 0, 3, 0, 3, 0, 3, 0],
        #     [3, 0, 3, 0, 3, 0, 3, 0, 3],
        #     [0, 3, 0, 3, 0, 3, 0, 2, 0],
        #     [3, 0, 3, 0, 3, 0, 2, 0, 2],
        #     [0, 3, 0, 3, 0, 3, 0, 2, 0],
        #     [3, 0, 3, 0, 1, 0, 2, 0, 2],
        #     [0, 3, 0, 1, 0, 1, 0, 2, 0],
        #     [0, 0, 3, 0, 1, 0, 3, 0, 0],
        #     [0, 0, 0, 1, 0, 1, 0, 0, 0],
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        # ]
        # ALIEN
        initial_board = [
             [0, 0, 0, 0, 2, 0, 0, 0, 0],
             [0, 0, 0, 3, 0, 3, 0, 0, 0],
             [0, 0, 2, 0, 2, 0, 3, 0, 0],
             [0, 3, 0, 1, 0, 2, 0, 3, 0],
             [2, 0, 1, 0, 1, 0, 3, 0, 3],
             [0, 2, 0, 2, 0, 3, 0, 3, 0],
             [3, 0, 1, 0, 2, 0, 3, 0, 3],
             [0, 2, 0, 2, 0, 3, 0, 3, 0],
             [3, 0, 3, 0, 3, 0, 3, 0, 3],
             [0, 3, 0, 3, 0, 1, 0, 1, 0],
             [3, 0, 3, 0, 1, 0, 2, 0, 3],
             [0, 3, 0, 3, 0, 1, 0, 1, 0],
             [3, 0, 3, 0, 2, 0, 2, 0, 1],
             [0, 3, 0, 1, 0, 2, 0, 3, 0],
             [0, 0, 3, 0, 1, 0, 1, 0, 0],
             [0, 0, 0, 3, 0, 3, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 0],
         ]
        # ETOILE
        # initial_board = [
        #     [0, 0, 0, 0, 1, 0, 0, 0, 0],
        #     [0, 0, 0, 3, 0, 3, 0, 0, 0],
        #     [0, 0, 3, 0, 1, 0, 3, 0, 0],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [1, 0, 3, 0, 1, 0, 3, 0, 1],
        #     [0, 1, 0, 3, 0, 1, 0, 1, 0],
        #     [3, 0, 1, 0, 1, 0, 1, 0, 3],
        #     [0, 3, 0, 1, 0, 1, 0, 3, 0],
        #     [3, 0, 1, 0, 3, 0, 2, 0, 3],
        #     [0, 3, 0, 2, 0, 2, 0, 3, 0],
        #     [3, 0, 2, 0, 2, 0, 2, 0, 3],
        #     [0, 2, 0, 2, 0, 3, 0, 2, 0],
        #     [2, 0, 3, 0, 2, 0, 3, 0, 2],
        #     [0, 3, 0, 3, 0, 3, 0, 3, 0],
        #     [0, 0, 3, 0, 2, 0, 3, 0, 0],
        #     [0, 0, 0, 3, 0, 3, 0, 0, 0],
        #     [0, 0, 0, 0, 2, 0, 0, 0, 0],
        # ]
        for i in range(dim[0]):
            for j in range(dim[1]):
                if initial_board[i][j] == W:
                    env[(i, j)] = Piece(piece_type=player1.get_piece_type(), owner=player1)
                elif initial_board[i][j] == B:
                    env[(i, j)] = Piece(piece_type=player2.get_piece_type(), owner=player2)
        init_rep = BoardAbalone(env=env, dim=dim)
        initial_game_state = GameStateAbalone(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep, step=0
        )

        master = MasterAbalone(
             name="Abalone", initial_game_state=initial_game_state, players_iterator=list_players, log_file="log.txt", port=16001
         )
        master.record_game()

run_multiple_games()
