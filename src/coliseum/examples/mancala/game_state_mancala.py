from typing import Dict, List, Set

from coliseum.examples.mancala.board_mancala import BoardMancala
from coliseum.examples.mancala.master_mancala import MasterMancala
from coliseum.game.action import Action
from coliseum.game.game_layout.board import Piece
from coliseum.game.game_state import GameState
from coliseum.player.player import Player
from coliseum.utils.custom_exceptions import ActionNotPermittedError

BOARD_SIZE = 6

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
        """
        Returns a set of all possible actions from this game state

        Raises:
            ActionNotPermittedError: if the action is not permitted

        Returns:
            Set[Action]: a set of possible actions
        """
        next_player = self.get_next_player().get_id()
        actions = []
        if next_player == 0:
            for i in range(1,7):
                if len(self.rep.env[(0,i)]) != 0:
                    actions.append(self.generate_action((0,i)))
        else:
            for i in range(1,7):
                if len(self.rep.env[(1,i-1)]) != 0:
                    actions.append(self.generate_action((1,i-1)))
        return Set(actions)

    def generate_action(self, pool):
        """
        Generate an action (next_gs) from a pool

        Args:
            pool (Tuple): the pool to play

        Raises:
            ActionNotPermittedError: _description_

        Returns:
            Action: _description_
        """
        if len(self.rep.env[pool]) == 0:
            raise ActionNotPermittedError("Pool "+str(pool)+" is empty")
        env = self.rep.copy().get_env()
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
            elif pool[0] == 1 and pool[1] < BOARD_SIZE and player == 1:
                front = (0,pool[1]+1)
                if len(env[front]) > 0:
                    env[(1,6)] += env[front]
                    env[front] = []
                    env[pool] = []
        # if one side is empty, win all the pieces in front
        player0_done = True
        player1_done = True
        for i in range(1,7):
            if len(env[(0,i)]) != 0:
                player0_done = False
            if len(env[(1,i-1)]) != 0:
                player1_done = False
        if player0_done:
            for i in range(1,7):
                if len(env[(1,i-1)]) > 0:
                    env[(1,6)] += env[(1,i-1)]
                    env[(1,i-1)] = []
        if player1_done:
            for i in range(1,7):
                if len(env[(0,i)]) > 0:
                    env[(0,0)] += env[(0,i)]
                    env[(0,i)] = []

        new_gs = GameStateMancala(self.compute_scores(env),MasterMancala.get_next_player(self.get_next_player(),self.get_players(),self.rep.get_env(),env),self.players,BoardMancala(env))

        return Action(self.copy(), new_gs)

    def get_next_pool(self, pool, player):
        """
        Get the next pool to play

        Args:
            pool (Tuple): the pool to play
            player (int): the player to play

        Raises:
            Exception: _description_

        Returns:
            Tuple: the next pool to play
        """
        if pool[0] == 0 and pool[1] > 0:
            next_pool = (0,pool[1]-1)
        elif pool[0] == 0 and pool[1] == 0:
            next_pool = (1,0)
        elif pool[0] == 1 and pool[1] < BOARD_SIZE:
            next_pool = (1,pool[1]+1)
        elif pool[0] == 1 and pool[1] == BOARD_SIZE:
            next_pool = (0,6)
        else:
            raise Exception("Pool"+str(pool)+"is not valid")
        if (player == 0 and next_pool == (1,6)) or (player == 1 and next_pool == (0,0)):
            next_pool = self.get_next_pool(next_pool,player)
        return next_pool

    def compute_scores(self, env):
        """
        Compute the scores of the game

        Args:
            env (Dict): the next environment

        Returns:
            Dict: the scores of the game
        """
        scores = {0:len(env[(0,0)]),1:len(env[(1,6)])}
        return scores

    def __hash__(self) -> int:
        return hash(frozenset([(hash(pos),hash(len(piece))) for pos,piece in self.rep.get_env().items()]))

    def copy(self):
        return GameStateMancala(self.scores,self.next_player,self.players,self.rep.copy())
