import time
from coliseum.examples.avalam.board_avalam import BoardAvalam, PieceAvalam
from coliseum.examples.avalam.game_state_avalam import GameStateAvalam
from coliseum.examples.avalam.random_player_avalam import RandomPlayerAvalam
from coliseum.player.player import LocalPlayerProxy

player1 = LocalPlayerProxy(RandomPlayerAvalam("R", name="louis"))
player2 = LocalPlayerProxy(RandomPlayerAvalam("Y", name="loic"))

list_players = [player1, player2]
init_scores = {player1.get_id(): 0, player2.get_id(): 0}
dim = [9, 9]
env = {}
initial_board = [
    [0, 0, 1, -1, 0, 0, 0, 0, 0],
    [0, 1, -1, 1, -1, 0, 0, 0, 0],
    [0, -1, 1, -1, 1, -1, 1, 0, 0],
    [0, 1, -1, 1, -1, 1, -1, 1, -1],
    [1, -1, 1, -1, 0, -1, 1, -1, 1],
    [-1, 1, -1, 1, -1, 1, -1, 1, 0],
    [0, 0, 1, -1, 1, -1, 1, -1, 0],
    [0, 0, 0, 0, -1, 1, -1, 1, 0],
    [0, 0, 0, 0, 0, -1, 1, 0, 0],
]
for i in range(dim[0]):
    for j in range(dim[1]):
        if initial_board[i][j] == 1:
            env[(i, j)] = PieceAvalam(piece_type=player1.get_piece_type(), owner=player1, value=1)
            init_scores[player1.get_id()] += 1
        elif initial_board[i][j] == -1:
            env[(i, j)] = PieceAvalam(piece_type=player2.get_piece_type(), owner=player2, value=1)
            init_scores[player2.get_id()] += 1

init_rep = BoardAvalam(env=env, dim=dim)

initial_game_state = GameStateAvalam(
            scores=init_scores, next_player=player1, players=list_players, rep=init_rep
        )
test = 0
def explore(board, depth):
    global test
    if depth == 0:
        test += 1
        return 
    for action in board.get_possible_actions():
        #print(action.get_new_gs().get_rep())
        explore(action.get_new_gs(), depth-1)
    return

start = time.time()
e = explore(initial_game_state, 3)
end = time.time()
print(end - start)
print(test)