from typing import Dict, Iterable
from coliseum.examples.tictactoe.board_tictac import BoardTictac
from coliseum.game.game_state import GameState
from coliseum.player.player import Player
from coliseum.game.master import GameMaster


class MasterTictac(GameMaster):
    """
    Master to play the game Tic Tac Toe

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

    def compute_scores(self, representation: BoardTictac) -> dict[int, float]:
        """
        Function to compute the score of each player in a list

        Args:
            representation (BoardTictac): current representation of the game state

        Returns:
            dict[int,float]: return a dictionnary with id_player: score
        """
        scores = {}
        for player in self.players:
            _, pieces = representation.get_pieces_player(player)
            # TODO print(pieces)
            if len(pieces) < representation.get_dimensions()[0]:
                scores[player.get_id()] = 0.0
            else:
                success = False
                env = representation.get_env()
                dim = representation.get_dimensions()[0]
                for i in range(dim):
                    counter = 0.0
                    for j in range(dim):
                        if env.get((i, j), None) and env.get((i, j), None).get_owner_id() == player.get_id():
                            counter += 1.0
                    if counter > 2.0:
                        scores[player.get_id()] = 1.0
                        success = True
                if success == True:
                    continue
                for i in range(dim):
                    counter = 0.0
                    for j in range(dim):
                        if env.get((j, i), None) and env.get((j, i), None).get_owner_id() == player.get_id():
                            counter += 1.0
                    if counter > 2.0:
                        scores[player.get_id()] = 1.0
                        success = True
                if success == True:
                    continue
                counter = 0.0
                for i in range(dim):
                    if env.get((i, i), None) and env.get((i, i), None).get_owner_id() == player.get_id():
                        counter += 1.0
                if counter > 2.0:
                    scores[player.get_id()] = 1.0
                    success = True
                if success == True:
                    continue
                counter = 0.0
                for i in range(dim):
                    if (
                        env.get((i, dim - 1 - i), None)
                        and env.get((i, dim - 1 - i), None).get_owner_id() == player.get_id()
                    ):
                        counter += 1.0
                if counter > 2.0:
                    scores[player.get_id()] = 1.0
                    success = True
                if success == True:
                    continue
                else:
                    scores[player.get_id()] = 0.0
        # TODO print(scores)
        return scores

    def compute_winner(self, scores: Dict[int, float]) -> Iterable[Player]:
        """Computes the winners of the game based on the scores

        Args:
            scores (Dict[int, float]): score for each player

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Iterable[Player]: list of the player who won the game
        """
        max_val = max(scores.values())
        players_id = list(filter(lambda key: scores[key] == max_val, scores))
        iter = filter(lambda x: x.get_id() in players_id, self.players)
        return iter
