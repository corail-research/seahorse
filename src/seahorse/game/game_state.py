from abc import abstractmethod
from collections.abc import Generator
from itertools import cycle
from typing import Any

from seahorse.game.action import Action
from seahorse.game.representation import Representation
from seahorse.game.stateful_action import StatefulAction
from seahorse.game.stateless_action import StatelessAction
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.utils.serializer import Serializable


class GameState(Serializable):
    """
    A class representing the game state.

    Attributes:
        scores (Dict[int, Any]): The scores of the state for each player.
        active_player (Player): The player who can perform an action on the game state.
        players (List[Player]): The list of players.
        rep (Representation): The representation of the game.
    """

    def __init__(self, scores: dict[int, Any], active_player: Player,
                 players: list[Player], rep: Representation) -> None:
        """
        Initializes a new instance of the GameState class.

        Args:
            scores (Dict[int, Any]): The scores of the state for each player.
            active_player (Player): The player who can perform an action on the game state.
            players (List[Player]): The list of players.
            rep (Representation): The representation of the game.
        """
        self.scores = scores

        # if not isinstance(next_player, Player):
        #     msg = "Players object should be provided as Player type to ensure it can be serialized"
        #     raise ValueError(msg)
        self.active_player = active_player

        # if not all(isinstance(player, Player) for player in players):
        #     msg = "Players object should be provided as Player type to ensure it can be serialized"
        #     raise ValueError(msg)
        self.players = players

        self.rep = rep
        self._possible_stateless_actions = None
        self._possible_stateful_actions = None

    def get_player_score(self, player: Player) -> float:
        """
        Gets a player's score.

        Args:
            player (Player): The player.

        Returns:
            float: The score.
        """
        return self.scores[player.get_id()]

    def get_active_player(self) -> Player:
        """
        Returns the active player who can perform an action on the game state.

        Returns:
            Player: The next player.
        """
        return self.active_player

    def compute_next_player(self) -> Player:
        """
        Computes the player who's gonna play on the next game state.

        Returns:
            Player: The next player.
        """
        if len(self.players) > 1:
            current = self.active_player
            curr_id = self.players.index(current)
            return next(cycle(self.players[curr_id + 1 :] + self.players[:curr_id]))

        return self.active_player

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

    def get_possible_stateless_actions(self) -> frozenset[StatelessAction]:
        """
        Returns a copy of the possible stateless actions from this state.
        The first call triggers the `generate_possible_stateless_actions` method.

        Returns:
            FrozenSet[StatelessAction]: The possible actions.
        """
        # Lazy loading
        if self.is_done():
            return frozenset()
        if self._possible_stateless_actions is None:
            self._possible_stateless_actions = frozenset(self.generate_possible_stateless_actions())
        return self._possible_stateless_actions

    def get_possible_stateful_actions(self) -> frozenset[StatefulAction]:
        """
        Returns a copy of the possible stateful actions from this state.
        The first call triggers the `generate_possible_stateful_actions` method.

        Returns:
            FrozenSet[StatefulAction]: The possible actions.
        """
        # Lazy loading
        if self.is_done():
            return frozenset()
        if self._possible_stateful_actions is None:
            self._possible_stateful_actions = frozenset(self.generate_possible_stateful_actions())
        return self._possible_stateful_actions

    def check_action(self, action: Action) -> bool:
        """
        Checks if an action is feasible.

        Args:
            action (Action): The action to check.

        Returns:
            bool: True if the action is feasible, False otherwise.
        """
        if isinstance(action, StatelessAction):
            return action in self.get_possible_stateless_actions()
        if isinstance(action, StatefulAction):
            return action in self.get_possible_stateful_actions()
        return False

    def convert_gui_data_to_action_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Converts GUI data to stateless action data.
        This method can and should be overridden by the user.

        Args:
            data (Dict[str, Any]): The GUI data.

        Returns:
            Dict[str, Any]: The action data.
        """
        return data

    @abstractmethod
    def apply_action(self, action: StatelessAction) -> "GameState":
        """
        Applies an action to the game state.

        Args:
            action (StatelessAction): The action to apply.

        Returns:
            GameState: The new game state.

        Raises:
            MethodNotImplementedError: If the method is not implemented.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def generate_possible_stateless_actions(self) -> Generator[StatelessAction, None, None]:
        """
        Generates all possible stateless actions from this game state.

        Returns:
            Generator[StatelessAction]: A generator of possible stateless actions.

        Raises:
            MethodNotImplementedError: If the method is not implemented.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def generate_possible_stateful_actions(self) -> Generator[StatefulAction, None, None]:
        """
        Generates all possible stateful actions from this game state.

        Returns:
            Generator[StatefulAction]: A generator of possible stateful actions.

        Raises:
            MethodNotImplementedError: If the method is not implemented.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def convert_stateful_action_to_stateless_action(self, stateful_action: StatefulAction) -> StatelessAction:
        """
        Converts a stateful action to a stateless action.

        Args:
            action (StatefulAction): The stateful action to convert.

        Returns:
            StatelessAction: The converted stateless action.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def compute_scores(self, play_info: Any) -> dict[int, Any]:
        """
        Computes the scores of each player.

        Args:
            play_info (Any): Information about the play used to compute scores.

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
        to_print += f"Next person to play is player {self.get_active_player().get_id()} ({self.get_active_player().get_name()}).\n"
        return to_print

    @classmethod
    @abstractmethod
    def from_json(cls,data:str,*,next_player:Player | None = None) -> "GameState":
        raise MethodNotImplementedError()
