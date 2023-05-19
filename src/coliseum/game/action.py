from coliseum.game.representation import Representation


class Action:
    """
    Attributes:
        past_rep (Representation): past representation of the game
        new_rep (Representation): new representation of the game
    """

    def __init__(self,
                 past_rep: Representation,
                 new_rep: Representation
                 ) -> None:
        self.past_rep = past_rep
        self.new_rep = new_rep

    def get_past_rep(self):
        """
        Returns:
            Representation: past_rep
        """
        return self.past_rep

    def get_new_rep(self):
        """
        Returns:
            Representation: new_rep
        """
        return self.new_rep
