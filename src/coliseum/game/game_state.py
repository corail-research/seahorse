from abc import abstractmethod
from typing import Dict, FrozenSet, List, Set

from coliseum.game.action import Action
from coliseum.game.representation import Representation
from coliseum.player.player import Player
from coliseum.utils.custom_exceptions import MethodNotImplementedError


class GameState:
    """
    Attributes:
        score (Dict[player_id->float]): scores of the state for each players
        next_player (Player): next player to play
        players (list[Player]): list of players
        rep (Representation): representation of the game
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: Representation) -> None:
        self.scores = scores
        self.next_player = next_player
        self.players = players
        self.rep = rep
        self._possible_actions = None

    def get_player_score(self, player: Player) -> float:
        """
        Gets a player's score

        Args:
            player (Player): -

        Returns:
            float: the score
        """
        return self.scores[player.get_id()]

    def get_next_player(self) -> Player:
        """
        Returns:
            Player: next_player
        """
        if not self.is_done():
            return self.next_player

    def get_scores(self) -> Dict:
        """
        Returns:
            Dict: player_id->score
        """
        return self.scores

    def get_players(self):
        """
        Returns:
            list[Player]: players
        """
        return self.players

    def get_rep(self):
        """
        Returns:
            Representation: rep
        """
        return self.rep

    def get_possible_actions(self) -> FrozenSet[Action]:
        """
        Returns a copy of the possible actions from this state
        First call triggers `generate_possible_actions`

        Returns:
            Set[Action]: the possible actions
        """
        # Lazy loading
        if self._possible_actions is None:
            self._possible_actions = frozenset(self.generate_possible_actions())
        return self._possible_actions


    def check_action(self, action: Action) -> bool:
        """
        Function to know if an action is feasible

        Args:
            action (Action): -

        Returns:
            bool: -
        """

        if action in self.get_possible_actions():
            return True
        return False

    @abstractmethod
    def generate_possible_actions(self) -> Set[Action]:
        """
        Returns a set of all possible actions from this game state

        Args:
            rep (Representation): representation of the current state

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            Set[Action]: a set of possible actions
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def is_done(self) -> bool:
        """
        Indicates if the current GameState is final.

        Raises:
            MethodNotImplementedError: _description_

        Returns:
            bool: `True` if the state is final `False` else
        """
        raise MethodNotImplementedError()

    def __str__(self) -> str:
        to_print = f"Current scores are {self.get_scores()}.\n"
        to_print += (
            f"Next person to play is player {self.get_next_player().get_id()} ({self.get_next_player().get_name()}).\n"
        )
        return to_print
