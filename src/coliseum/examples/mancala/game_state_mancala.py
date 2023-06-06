from typing import Dict, List, Set

from coliseum.src.coliseum.utils.custom_exceptions import ActionNotPermittedError
from coliseum.src.coliseum.game.action import Action
from coliseum.game.action import Action
from coliseum.game.game_layout.board import Piece
from coliseum.game.game_state import GameState
from coliseum.player.player import Player
from coliseum.examples.mancala.board_mancala import BoardMancala


class GameStateMancala(GameState):

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardMancala) -> None:
        super().__init__(scores, next_player, players, rep)

    def is_done(self) -> bool:
        """
        Returns:
            bool: True if the game is done
        """
        player1_done = True
        player2_done = True
        for i in range(1,7):
            if len(self.rep.env[(0,i)]) != 0:
                player1_done = False
            if len(self.rep.env[(1,i-1)]) != 0:
                player2_done = False
        return player1_done or player2_done
    
    def generate_possible_actions(self) -> Set[Action]:
        next_player = self.get_next_player().get_id()
        actions = []
        if next_player == 0:
            for i in range(1,7):
                if len(self.rep.env[(0,i)]) != 0:
                    actions.append(self.generateAction((0,i)))
        else:
            for i in range(1,7):
                if len(self.rep.env[(1,i-1)]) != 0:
                    actions.append(self.generateAction((1,i)))
        return actions
    
    def generateAction(self, pool):
        if len(self.rep.env[pool]) == 0:
            raise ActionNotPermittedError("Pool",pool,"is empty")
        env = self.rep.get_env()
        player = self.get_next_player().get_id()
        pieces = len(env[pool])
        env[pool] = []
        single_piece = Piece("rock", None)
        while pieces > 0:
            pool = self.get_next_pool(pool,player)
            env[pool].append(single_piece.copy())
            pieces -= 1
        # if stop on empty, win all the pieces in front    
        if len(env[pool]) == 1:
            if pool[0] == 0 and pool[1] > 0 and player == 0:
                front = (1,pool[1]-1)
                if len(env[front]) > 0:
                    env[(0,0)] += env[front]
                    env[front] = []
                    env[pool] = []
            elif pool[0] == 1 and pool[1] < 6 and player == 1:
                front = (0,pool[1]+1)
                if len(env[front]) > 0:
                    env[(1,6)] += env[front]
                    env[front] = []
                    env[pool] = []
        # if stop on own pool, play again
        if player == 0 and pool == (0,0):
            pass

        return Action(self.rep, BoardMancala(env))
    
    def get_next_pool(self, pool, player):
        if pool[0] == 0 and pool[1] > 0:
            next_pool = (0,pool[1]-1)
        elif pool[0] == 0 and pool[1] == 0:
            next_pool = (1,0)
        elif pool[0] == 1 and pool[1] < 6:
            next_pool = (1,pool[1]+1)
        elif pool[0] == 1 and pool[1] == 6:
            next_pool = (0,6)
        else:
            raise Exception("Pool",pool,"is not valid")
        if (player == 0 and next_pool == (1,6)) or (player == 1 and next_pool == (0,0)):
            next_pool = self.get_next_pool(next_pool,player)
        return next_pool
                    