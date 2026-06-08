from __future__ import annotations

import json
from typing import TYPE_CHECKING

from seahorse.game.representation import Representation
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.player.player import Player


class Piece(Serializable):
    """
    Represents a game piece with ownership and type information.

    The Piece class encapsulates all information about a game piece,
    including its type and which player owns it. This class is serializable
    and can be used in any board game where pieces have ownership.

    **Relationship to Game State**:

    - Pieces are stored in the [Board][..Board]'s environment dictionary
    - Used by [GameState][....game_state.GameState]
      for state transitions and display
    - Ownership information is critical for game logic

    Attributes:
        piece_type (str):
            The type/category of the piece (e.g., "king", "queen", "soldier").
        owner_id (int):
            The ID of the player who owns this piece.
    """

    def __init__(self, piece_type: str, owner: Player | None = None,
                 owner_id: int = -1) -> None:
        """
        Initializes a new Piece instance.

        Args:
            piece_type (str):
                The type/category of the piece.
            owner (Player | None):
                The Player object who owns this piece.
                If None, owner_id must be provided or defaults to -1.
            owner_id (int):
                Alternative way to specify owner by ID.
                Defaults to -1 (no owner).
        """
        self.piece_type = piece_type
        if owner is None:
            self.owner_id = owner_id
        else:
            self.owner_id = owner.get_id()

    def get_type(self) -> str:
        """
        Retrieves the type/category of the piece.

        Returns:
            str: The piece type (e.g., "king", "queen", "soldier").
        """
        return self.piece_type

    def get_owner_id(self) -> int:
        """
        Retrieves the ID of the player who owns this piece.

        Returns:
            int: Owner's player ID, or -1 if the piece has no owner.
        """
        return self.owner_id

    def copy(self, no_owner: bool = True) -> Piece:
        """
        Creates a deep copy of the piece.
        Copy can be created with or without owner reference.

        Args:
            no_owner (bool):
                If True, the Piece copy will have no owner.
                Defaults to True.

        Returns:
            Piece: A new Piece instance with the same type.
        """
        if no_owner:
            return Piece(self.piece_type)
        else:
            return Piece(self.piece_type, owner_id=self.owner_id)

    def __hash__(self) -> int:
        """
        Computes a hash based on piece type and owner.

        Returns:
            int: Hash value.
        """
        return hash((hash(self.get_type()), hash(self.owner_id)))

    def __eq__(self, other: Piece) -> bool:
        """
        Compares two pieces for equality.

        Args:
            other (Piece): Other Piece to compare with.

        Raises:
            ValueError: If other object is not a Piece.

        Returns:
            bool: True if both pieces have the same type and owner,
                False otherwise.
        """
        if not isinstance(other, Piece):
            raise ValueError("Must compare two Piece object for equality")
        return hash(self) == hash(other)

    def to_json(self) -> dict:
        """
        Serializes the piece to a JSON-compatible dictionary.

        Returns:
            dict: Dictionary containing piece_type and owner_id.
        """
        return self.__dict__

    @classmethod
    def from_json(cls, data: str | dict, **_kwargs) -> Serializable:
        """
        Deserializes a Piece from JSON data.

        Args:
            data (str | dict):
                JSON string or dict containing serialized piece data.

        Returns:
            Piece: Deserialized Piece instance.
        """
        if isinstance(str, data):
            return cls(**json.loads(data))
        return cls(**data)


class Board(Representation):
    """
    A specialized [Representation][....representation.Representation]
    for board games with grid-based layouts.

    The Board class provide board-specific functionality for games
    with grid-based layouts (e.g, chess, checkers, go).
    It maintains a mapping of positions to pieces and provides utilities
    for board operations and piece management.

    Attributes:
        env (dict[tuple[int, int], Piece]): Dictionary mapping board positions
            (as (row, col) tuples) to Piece objects at those positions.
        dimensions (list[int]): Board dimensions as [rows, columns].
    """

    def __init__(self, env: dict[tuple[int], Piece], dim: list[int]) -> None:
        """
        Initializes a new Board instance.

        Args:
            env (dict[tuple[int], Piece]): Dictionary mapping positions
                to pieces. Empty positions should be omitted (not stored
                with None values).
            dim (list[int]): Board dimensions as [rows, columns].

        Note:
            - Positions are (row, column) tuples with 0-based indexing
            - Empty positions are represented by absence from the dictionary
            - This is more memory-efficient than storing None for empty cells
        """
        super().__init__(env)
        self.dimensions = dim

    def get_dimensions(self) -> list[int]:
        """
        Retrieves the board dimensions.

        Returns:
            list[int]: List containing [rows, columns] dimensions.
        """
        return self.dimensions

    def get_pieces_player(self, owner: Player) -> tuple[int, list[Piece]]:
        """
        Retrieves all pieces owned by a specific player.

        Args:
            owner (Player): The player whose pieces to retrieve.

        Returns:
            tuple[int, list[Piece]]: A tuple containing:
                - int: Count of pieces owned by the player
                - list[Piece]: List of Piece objects owned by the player

        Note:
            This method iterates through all positions on the board.
            For large boards, consider caching this information if
            called frequently.
        """
        pieces_list = []
        number = 0
        for key in self.env.keys():
            if self.env[key].get_owner_id() == owner.get_id():
                number += 1
                pieces_list.append(key)
        return number, pieces_list

    def __hash__(self) -> int:
        """
        Computes a hash based on board state (positions and pieces).

        Returns:
            int: Hash value of the board state.
        """
        return hash(frozenset([(hash(pos), hash(piece))
                               for pos, piece in self.env.items()]))

    def __eq__(self, other: Board) -> bool:
        """
        Compares two boards for equality.

        Args:
            other (Board): Other Board to compare with.

        Raises:
            ValueError: If other object is not a Board.

        Returns:
            bool: True if both boards have the same pieces at the same
                positions, False otherwise.
        """
        if not isinstance(other, Board):
            raise ValueError("Must compare two Board object for equality")
        return hash(self) == hash(other)

    def __str__(self) -> str:
        """
        Creates a human-readable ASCII representation of the board.

        Returns:
            str:
                Grid representation with pieces as their type
                and empty cells as underscores.

        Example:
            Small 3x3 board with two [piece][...Piece].

            ``` python
            >>> board = Board({(0,0): Piece("R"), (1,1): Piece("P")}, [3,3])
            >>> print(board)
            R _ _
            _ P _
            _ _ _
            ```
        """
        dim = self.get_dimensions()
        to_print = ""
        for i in range(dim[0]):
            for j in range(dim[1]):
                if self.get_env().get((i, j), -1) != -1:
                    to_print += str(self.get_env()[(i, j)].get_type()) + " "
                else:
                    to_print += "_ "
            to_print += "\n"
        return to_print
