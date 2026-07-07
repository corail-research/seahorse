from __future__ import annotations

from abc import abstractmethod

from seahorse.utils.serializer import Serializable


class Action(Serializable):
    """
    Abstract class representing an action in a game.

    An Action represents a move or decision that a player can make during
    their turn. This class is serializable and must be extended to create
    game-specific actions.

    **Class Hierarchy**:
    ```
    Action (abstract)
    ├── StatefulAction (concrete, for generic representation)
    └── StatelessAction (concrete, for performance and transmission)
    ```

    **Design Philosophy**:
        - [StatefulAction][seahorse.game.stateful_action.StatefulAction] provides a complete, self-contained representation.
        - [StatelessAction][seahorse.game.stateless_action.StatelessAction] offers a lightweight alternative.
    """

    @abstractmethod
    def get_stateful_action(self, *args, **kwargs) -> Action:
        """
        Converts this action to a stateful action with game context.

        This abstract method must be implemented by subclasses to create
        a version of the action that includes game state information,
        enabling validation and execution within the current game context.

        Args:
            *args (tuple[_, ...]): Variable length argument list.
                Typically includes:
                - game_state (GameState): The current state of the game.
            **kwargs (dict[str, _]): Arbitrary keyword arguments.

        Returns:
            StatefulAction: A stateful action object that can be validated and
                executed within a game state context.

        Raises:
            NotImplementedError: If not implemented in the subclass.

        Note:
            This method is called by the GameMaster to convert player actions
            to a form that can be validated against the current game state.
        """
        raise NotImplementedError
