from coliseum.player.player import Player


class PlayerTictac(Player):
    """
    Attributes:
        id_player (int): id of the player
        name (str): name of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        super().__init__(name)
        self.piece_type = piece_type

    def get_piece_type(self):
        """
        Returns:
            piece_type: string to represent the type of the piece
        """
        return self.piece_type

    def __str__(self) -> str:
        return super().__str__()
