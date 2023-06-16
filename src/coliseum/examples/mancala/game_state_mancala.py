from typing import Dict, List, Set

from coliseum.examples.mancala.board_mancala import BoardMancala
from coliseum.examples.mancala.master_mancala import MasterMancala
from coliseum.game.action import Action
from coliseum.game.game_layout.board import Piece
from coliseum.game.game_state import GameState
from coliseum.game.representation import Representation
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
        return actions

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
                    env[(0,0)].append(single_piece.copy())
                    env[front] = []
                    env[pool] = []
            elif pool[0] == 1 and pool[1] < BOARD_SIZE and player == 1:
                front = (0,pool[1]+1)
                if len(env[front]) > 0:
                    env[(1,6)] += env[front]
                    env[(1,6)].append(single_piece.copy())
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

        new_gs = GameStateMancala(self.compute_scores(env),self.compute_next_player(self.get_next_player(),self.rep.get_env(),env),self.players,BoardMancala(env))

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
        scores = {self.players[0].get_id():len(env[(0,0)]), self.players[1].get_id():len(env[(1,6)])}
        return scores

    def replay(self, player: Player, current_rep: Representation, next_rep: Representation) -> bool:
        """Determine if the player can replay

        Args:
            player (Player): _description_
            current_rep (Representation): _description_
            next_rep (Representation): _description_

        Returns:
            bool: True if the player can replay
        """
        if player.get_id() == 0:
            for i in range(1,7):
                if len(current_rep[(0,i)]) > len(next_rep[(0,i)]) and (len(current_rep[(0,i)]) - i)%13 == 0:
                    return True
        else:
            for i in range(0,6):
                if len(current_rep[(1,i)]) > len(next_rep[(1,i)]) and (len(current_rep[(1,i)]) - (6-i))%13 == 0:
                    return True

    def compute_next_player(self, player: Player, current_rep: Representation = None, next_rep: Representation = None) -> Player:
        """Function to get the next player, by default it is the next player in the list but if the player can replay it is the same player

        Args:
            player (Player): current player
            players_list (List[Player]): list of players
            current_rep (Representation, optional): current representation of the game. Defaults to None.
            next_rep (Representation, optional): next representation of the game. Defaults to None.

        Returns:
            Player: next player
        """
        if self.replay(player, current_rep, next_rep):
            return player
        return self.get_next_player()

    def __hash__(self) -> int:
        return hash(frozenset([(hash(pos),hash(len(piece))) for pos,piece in self.rep.get_env().items()]))

    def copy(self):
        return GameStateMancala(self.scores,self.next_player,self.players,self.rep.copy())
