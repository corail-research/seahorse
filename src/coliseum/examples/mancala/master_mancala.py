from typing import Dict, Iterable, List

from coliseum.game.game_state import GameState
from coliseum.game.master import GameMaster
from coliseum.game.representation import Representation
from coliseum.player.player import Player


class MasterMancala(GameMaster):

    def __init__(
        self, name: str, initial_game_state: GameState, players_iterator: Iterable[Player], log_file: str
    ) -> None:
        super().__init__(name, initial_game_state, players_iterator, log_file)

    @staticmethod
    def replay(player: Player, current_rep: Representation, next_rep: Representation) -> bool:
        """Determine if the player can replay

        Args:
            player (Player): _description_
            current_rep (Representation): _description_
            next_rep (Representation): _description_

        Returns:
            bool: True if the player can replay
        """
        if player.get_id() == 0:
            for i in range(1,7):
                if len(current_rep[(0,i)]) > len(next_rep[(0,i)]) and (len(current_rep[(0,i)]) - i)%13 == 0:
                    return True
        else:
            for i in range(0,6):
                if len(current_rep[(1,i)]) > len(next_rep[(1,i)]) and (len(current_rep[(1,i)]) - (6-i))%13 == 0:
                    return True

    @staticmethod
    def get_next_player(player: Player, players_list: List[Player], current_rep: Representation = None, next_rep: Representation = None) -> Player:
        """Function to get the next player, by default it is the next player in the list but if the player can replay it is the same player

        Args:
            player (Player): current player
            players_list (List[Player]): list of players
            current_rep (Representation, optional): current representation of the game. Defaults to None.
            next_rep (Representation, optional): next representation of the game. Defaults to None.

        Returns:
            Player: next player
        """
        if MasterMancala.replay(player, current_rep, next_rep):
            return player
        return GameMaster.get_next_player(player, players_list)


    def compute_winner(self, scores: Dict[int, float]) -> Iterable[Player]:
        """Computes the winners of the game based on the scores

        Args:
            scores (Dict[int, float]): score for each player

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Iterable[Player]: list of the player who won the game
        """
        if scores[0] > scores[1]:
            return [p for p in self.players if p.get_id() == 0]
        elif scores[0] < scores[1]:
            return [p for p in self.players if p.get_id() == 1]
