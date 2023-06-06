from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coliseum.game.game_state import GameState


class Action:
    """
    Attributes:
        past_gs (Representation): past gsresentation of the game
        new_gs (Representation): new gsresentation of the game
    """

    def __init__(self, past_gs: GameState, new_gs: GameState) -> None:
        self.past_gs = past_gs
        self.new_gs = new_gs

    def get_past_gs(self) -> GameState:
        """
        Returns:
            Representation: past_gs
        """
        return self.past_gs

    def get_new_gs(self) -> GameState:
        """
        Returns:
            Representation: new_gs
        """
        return self.new_gs

    def __hash__(self):
        return hash((hash(self.get_new_gs()),hash(self.get_past_gs())))

    def __eq__(self, __value: object) -> bool:
        return hash(self)==hash(__value)

    def __str__(self):
        return "From:\n"+self.get_past_gs().get_rep().__str__()+"\nto:\n"+self.get_new_gs().get_rep().__str__()
