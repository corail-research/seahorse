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
    Abstract base class representing a game state.

    The GameState class encapsulates all information about the current state
    of a game, including scores, active player, and game representation.
    It serves as the foundation for game state management and transition logic.


    **For Game Designers**:
        MUST extend this class and implement all abstract methods
        to define game-specific logic and rules.

    Attributes:
        scores (dict[int, Any]):
            Current scores for each player, keyed by player ID.
        active_player (Player):
            Player whose turn it is to move.
        players (list[Player]):
            All players participating in the game.
        rep (Representation):
            Visual/abstract representation of the game state.
    """

    def __init__(self, scores: dict[int, Any], active_player: Player,
                 players: list[Player], rep: Representation) -> None:
        """
        Initializes a new instance of the GameState class.

        Args:
            scores (dict[int, Any]):
                The scores of the state for each player,
                mapping player IDs to score values.
            active_player (Player): Player who is currently active
                (whose turn it is).
            players (list[Player]): Complete list of players in the game.
            rep (Representation):
                State representation data for both game logic and display.
        """
        # TODO: A lot of games don't implement a straight score value at every state.
        # It should maybe become non mandatory to implement a score for those games.
        # Scores can then be part of the custom stats of a game.
        self.scores = scores
        self.active_player = active_player
        self.players = players

        self.rep = rep
        self._possible_stateless_actions = None
        self._possible_stateful_actions = None

    def get_player_score(self, player: Player) -> float:
        """
        Retrieves the current score for a specific player.

        Args:
            player (Player): The player whose score to retrieve.

        Returns:
            float: The player's current score.
        """
        return self.scores[player.get_id()]

    def get_active_player(self) -> Player:
        """
        Returns the active player who can perform an action on the game state.

        Returns:
            Player: The active player.
        """
        return self.active_player

    def compute_next_player(self) -> Player:
        """
        Computes which player should play next in turn order.

        Returns:
            Player: The next player in the turn sequence.
        """
        if len(self.players) > 1:
            current = self.active_player
            curr_id = self.players.index(current)
            return next(cycle(self.players[curr_id + 1:] + self.players[:curr_id]))

        return self.active_player

    def get_scores(self) -> dict[int, Any]:
        """
        Retrieves all player scores as a dictionary.

        Returns:
            dict[int, float]: Dictionary mapping player IDs to their scores.
        """
        return self.scores

    def get_players(self) -> list[Player]:
        """
        Returns the complete list of players in the game.

        Returns:
            list[Player]: List of all Player objects participating in the game.
        """
        return self.players

    def get_rep(self) -> Representation:
        """
        Retrieves the Representation containing game state data.

        Returns:
            Representation:
                The representation object containing
                both game logic and display data.
        """
        return self.rep

    def get_possible_stateless_actions(self) -> frozenset[StatelessAction]:
        """
        Returns all possible stateless actions from the current game state.

        Returns:
            frozenset[StatelessAction]:
                Immutable set of all valid stateless actions.

        Note:
            Uses lazy loading to generates actions only on first call.
            Returns empty set if game state is terminal.
        """
        # Lazy loading
        if self.is_done():
            return frozenset()
        if self._possible_stateless_actions is None:
            self._possible_stateless_actions = frozenset(
                self.generate_possible_stateless_actions())
        return self._possible_stateless_actions

    def get_possible_stateful_actions(self) -> frozenset[StatefulAction]:
        """
        Returns all possible stateful actions from the current game state.

        Returns:
            frozenset[StatefulAction]:
                Immutable set of all valid stateful actions.

        Note:
            Uses lazy loading to generates actions only on first call.
            Returns empty set if game state is terminal.
        """
        # Lazy loading
        if self.is_done():
            return frozenset()
        if self._possible_stateful_actions is None:
            self._possible_stateful_actions = frozenset(
                self.generate_possible_stateful_actions())
        return self._possible_stateful_actions

    def check_action(self, action: Action) -> bool:
        """
        Validates whether an action is legal in the current game state.

        Args:
            action (Action): The action to validate.

        Returns:
            bool: True if the action is legal, False otherwise.
        """
        if isinstance(action, StatelessAction):
            return action in self.get_possible_stateless_actions()
        if isinstance(action, StatefulAction):
            return action in self.get_possible_stateful_actions()
        return False

    # TODO: This function should be removed since we now have StatelessAction class.
    #      StatelessAction can encapsulate GUI data and convert it to StatefulAction.
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
        Applies a stateless action to create a new game state.

        **Abstract method - MUST be implemented by game designers**

        Args:
            action (StatelessAction): The stateless action to apply.

        Returns:
            GameState: A new GameState instance representing the result
                of applying the action.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - Must handle game-specific rules and state transitions.
            - Should compute new scores based on the action.
            - Must determine the next active player on specific case.
            - Should return a new GameState instance (immutable pattern).
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def generate_possible_stateless_actions(self) -> Generator[StatelessAction, None, None]:
        """
        Generates all possible stateless actions from the current state.

        **Abstract method - MUST be implemented by game designers**

        Returns:
            Generator[StatelessAction, None, None]: Generator yielding
                all legal stateless actions.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - Should generate actions based on game rules and current state
            - Use yield for memory efficiency with large action spaces
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def generate_possible_stateful_actions(self) -> Generator[StatefulAction, None, None]:
        """
        Generates all possible stateful actions from the current state.

        **Abstract method - MUST be implemented by game designers**

        Returns:
            Generator[StatefulAction, None, None]: Generator yielding 
                all legal stateful actions.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - Each StatefulAction must contain both current and resulting game states
            - Use yield for memory efficiency with large action spaces
        """
        raise MethodNotImplementedError()

    # TODO: We should see if this function is really necessary for general purpose.
    # It's not mandatory to maintain it if it's not the case since it's not used somewhere else in Seahorse.
    @abstractmethod
    def convert_stateful_action_to_stateless_action(self, stateful_action: StatefulAction) -> StatelessAction:
        """
        Converts a stateful action back to its stateless representation.

        **Abstract method - MUST be implemented by game designers**

        Args:
            stateful_action (StatefulAction): The stateful action to convert.

        Returns:
            StatelessAction: Equivalent stateless action representation.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - Essential for serialization and network transmission
            - Should extract minimal action data from the stateful action
            - The reverse operation of applying a stateless action
        """
        raise MethodNotImplementedError()

    # TODO: see TODO in init function.
    # If scores are non mandatory, this function should be removed.
    @abstractmethod
    def compute_scores(self, play_info: Any) -> dict[int, Any]:
        """
        Computes or updates player scores based on game progress.

        **Abstract method - MUST be implemented by game designers**

        Args:
            play_info (Any):
                Game-specific information needed to compute scores.

        Returns:
            dict[int, Any]: Updated scores for all players.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.
        """
        raise MethodNotImplementedError()

    @abstractmethod
    def is_done(self) -> bool:
        """
        Determines if the game state is terminal (game over).

        **Abstract method - MUST be implemented by game designers**

        Returns:
            bool: True if the game state is terminal, False otherwise.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - Terminal states have no legal actions
            - Should check win/lose/draw conditions based on game rules
            - Used by GameMaster to determine when to stop the game
        """
        raise MethodNotImplementedError()

    # TODO: see TODO in init function.
    # If scores are non mandatory, their hash should be removed.
    def __hash__(self) -> int:
        """
        Computes a hash value for the game state.

        Returns:
            int: Hash value based on scores and representation.

        Note:
            Used for caching and equality comparison. Game designers
            may need to override this for more precise hashing.
        """
        return hash((hash(frozenset(self.scores.items())), hash(self.rep)))

    def __eq__(self, value: "GameState") -> bool:
        """
        Compares two game states for equality.

        Args:
            value (GameState): Other game state to compare with.

        Returns:
            bool: True if both game states have the same hash, False otherwise.

        Note:
            Uses hash comparison for efficiency.
            Assumes well-behaved hash function with minimal collisions.
        """
        return hash(self) == hash(value)

    # TODO: see TODO in init function.
    # If scores are non mandatory, part of the string can be removed.
    def __str__(self) -> str:
        """
        Human-readable string representation of the game state.

        Returns:
            str: Formatted string showing scores and active player.
        """
        to_print = f"Current scores are {self.get_scores()}.\n"
        to_print += "Next person to play is player" \
            f"{self.get_active_player().get_id()} " \
            f"({self.get_active_player().get_name()}).\n"
        return to_print

    @classmethod
    @abstractmethod
    def from_json(cls, data: str, *, next_player: Player | None = None) -> "GameState":
        """
        Deserializes a GameState from JSON data.

        **Abstract method - MUST be implemented by game designers**

        Args:
            data (str): JSON string containing serialized game state.
            next_player (Player | None):
                Player to set as active after deserialization.

        Returns:
            GameState: Deserialized GameState instance.

        Raises:
            MethodNotImplementedError: If not implemented in subclass.

        Note:
            - Required for saving/loading game states
            - Must handle serialization of all game-specific attributes
            - Should work symmetrically with to_json() method from Serializable
        """
        raise MethodNotImplementedError()
