from coliseum.game.representation import Representation


class Action:
    """
    Attributes:
        past_rep (Representation): past representation of the game
        new_rep (Representation): new representation of the game
    """

    def __init__(self, past_rep: Representation, new_rep: Representation) -> None:
        self.past_rep = past_rep
        self.new_rep = new_rep

    def get_past_rep(self) -> Representation:
        """
        Returns:
            Representation: past_rep
        """
        return self.past_rep

    def get_new_rep(self) -> Representation:
        """
        Returns:
            Representation: new_rep
        """
        return self.new_rep

    def __hash__(self):
        return hash((hash(self.get_new_rep()),hash(self.get_past_rep())))

    def __eq__(self, __value: object) -> bool:
        return hash(self)==hash(__value)

    def __str__(self):
        return "From:\n"+self.get_past_rep().__str__()+"\nto:\n"+self.get_new_rep().__str__()
