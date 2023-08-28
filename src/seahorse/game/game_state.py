from abc import abstractmethod
from itertools import cycle
from typing import Any

from seahorse.game.action import Action
from seahorse.game.representation import Representation
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable


class GameState(Serializable):
    """
    A class representing the game state.

    Attributes:
        scores (Dict[int, Any]): The scores of the state for each player.
        next_player (Player): The next player to play.
        players (List[Player]): The list of players.
        rep (Representation): The representation of the game.
    """

    def __init__(self, scores: dict[int, Any], next_player: Player, players: list[Player], rep: Representation) -> None:
        """
        Initializes a new instance of the GameState class.

        Args:
            scores (Dict[int, Any]): The scores of the state for each player.
            next_player (Player): The next player to play.
            players (List[Player]): The list of players.
            rep (Representation): The representation of the game.
        """
        self.scores = scores
        self.next_player = next_player
        self.players = players
        self.rep = rep
        self._possible_actions = None

    def get_player_score(self, player: Player) -> float:
        """
        Gets a player's score.

        Args:
            player (Player): The player.

        Returns:
            float: The score.
        """
        return self.scores[player.get_id()]

    def get_next_player(self) -> Player:
        """
        Returns the next player.

        Returns:
            Player: The next player.
        """
        return self.next_player

    def compute_next_player(self) -> Player:
        """
        Computes the next player.

        Returns:
            Player: The next player.
        """
        current = self.next_player
        curr_id = self.players.index(current)
        return next(cycle(self.players[curr_id + 1 :] + self.players[:curr_id]))

    def get_scores(self) -> dict[int, float]:
        """
        Returns the scores.

        Returns:
            Dict: The player ID to score mapping.
        """
        return self.scores

    def get_players(self) -> list[Player]:
        """
        Returns the list of players.

        Returns:
            List[Player]: The list of players.
        """
        return self.players

    def get_rep(self) -> Representation:
        """
        Returns the representation of the game.

        Returns:
            Representation: The game representation.
        """
        return self.rep

    def get_possible_actions(self) -> frozenset[Action]:
        """
        Returns a copy of the possible actions from this state.
        The first call triggers the `generate_possible_actions` method.

        Returns:
            FrozenSet[Action]: The possible actions.
        """
        # Lazy loading
        if self.is_done():
            return frozenset()
        if self._possible_actions is None:
            self._possible_actions = frozenset(self.generate_possible_actions())
        return self._possible_actions

    def check_action(self, action: Action) -> bool:
        """
        Checks if an action is feasible.

        Args:
            action (Action): The action to check.

        Returns:
            bool: True if the action is feasible, False otherwise.
        """
        if action in self.get_possible_actions():
            return True
        return False

    @abstractmethod
    def convert_light_action_to_action(self,data) ->  Action :
        raise MethodNotImplementedError()

    @abstractmethod
    def generate_possible_actions(self) -> set[Action]:
        """
        Generates a set of all possible actions from this game state.

        Returns:
            Set[Action]: A set of possible actions.

        Raises:
            MethodNotImplementedError: If the method is not implemented.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def compute_scores(self, next_rep: Representation) -> dict[int, Any]:
        """
        Computes the scores of each player.

        Args:
            next_rep (Representation): The next representation.

        Returns:
            Dict[int, Any]: The scores of each player.

        Raises:
            MethodNotImplementedError: If the method is not implemented.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def is_done(self) -> bool:
        """
        Indicates if the current GameState is final.

        Returns:
            bool: True if the state is final, False otherwise.

        Raises:
            MethodNotImplementedError: If the method is not implemented.
        """
        raise MethodNotImplementedError()

    def __hash__(self) -> int:
        return hash((hash(frozenset(self.scores.items())), hash(self.rep)))

    def __eq__(self, value: object) -> bool:
        return hash(self) == hash(value)

    def __str__(self) -> str:
        to_print = f"Current scores are {self.get_scores()}.\n"
        to_print += f"Next person to play is player {self.get_next_player().get_id()} ({self.get_next_player().get_name()}).\n"
        return to_print
