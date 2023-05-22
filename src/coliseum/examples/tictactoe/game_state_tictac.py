from typing import Dict, List
from coliseum.game.game_state import GameState
from coliseum.game.representation import Representation
from coliseum.player.player import Player


class GameStateTictac(GameState) :
    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: Representation) -> None:
        super().__init__(scores, next_player, players, rep)
        
    def is_done(self) -> bool:
        if len(self.rep.get_env().keys()) == 9 :
            return True
        return False