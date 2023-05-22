from typing import Iterable, List
from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.game.game_state import GameState
from coliseum.player.player import Player
from src.coliseum.game.master import GameMaster


class MasterTictac(GameMaster):
    """Master to play the game Tic Tac Toe

    Attributes:
        name (str): name of the game
        initial_game_state (GameState): initial state of the game
        current_game_state (GameState): initial state of the game
        players_iterator (Iterable): an iterable for the players_iterator, ordered according
                            to the playing order. If a list is provided,
                            a cyclic iterator is automatically built
        log_file (str): name of the log file
    """
    def __init__(
        self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str
    ) -> None:
        super().__init__(name, initial_game_state, players_iterator, log_file)
        
    def compute_scores(self, representation: BoardTictac) -> dict[int,float]:
        scores = {}
        for player in self.players :
            score,_ = representation.get_pieces_player(player)
            scores[player.get_id()] = score
        return scores
            
