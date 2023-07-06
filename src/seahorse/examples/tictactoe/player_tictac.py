from seahorse.player.player import Player


class PlayerTictac(Player):
    """
    A player class for Tic Tac Toe.

    Attributes:
        piece_type (str): the type of the player.
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initializes a new instance of the PlayerTictac class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str): The name of the player.
        """
        super().__init__(name)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        """
        Returns:
            str: The type of the player's game piece.
        """
        return self.piece_type
