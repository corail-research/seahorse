from typing import Dict, List, Set

from coliseum.examples.mancala.board_mancala import BoardMancala
from coliseum.game.action import Action
from coliseum.game.game_layout.board import Piece
from coliseum.game.game_state import GameState
from coliseum.game.representation import Representation
from coliseum.player.player import Player
from coliseum.utils.custom_exceptions import ActionNotPermittedError

BOARD_SIZE = 6

class GameStateMancala(GameState):
    """
    Represents the game state of Mancala.

    Attributes:
        scores (Dict): Dictionary containing the scores of the game for each player.
        next_player (Player): Player object representing the next player.
        players (List[Player]): List of Player objects representing the players.
        rep (BoardMancala): BoardMancala object representing the game board.
    """

    def __init__(self, scores: Dict, next_player: Player, players: List[Player], rep: BoardMancala) -> None:
        """
        Initializes the GameStateMancala object.

        Args:
            scores (Dict): Dictionary containing the scores of the game for each player.
            next_player (Player): Player object representing the next player.
            players (List[Player]): List of Player objects representing the players.
            rep (BoardMancala): BoardMancala object representing the game board.
        """
        super().__init__(scores, next_player, players, rep)

    def is_done(self) -> bool:
        """
        Checks if the game is done.

        Returns:
            bool: True if the game is done, False otherwise.
        """
        player1_done = True
        player2_done = True
        for i in range(1, 7):
            if len(self.rep.env[(0, i)]) != 0:
                player1_done = False
            if len(self.rep.env[(1, i - 1)]) != 0:
                player2_done = False
        return player1_done or player2_done

    def generate_possible_actions(self) -> Set[Action]:
        """
        Generates all possible actions from the current game state.

        Raises:
            ActionNotPermittedError: If the action is not permitted.

        Returns:
            Set[Action]: Set of possible actions.
        """
        next_player = self.get_next_player().get_id()
        actions = []
        if next_player == 0:
            for i in range(1, 7):
                if len(self.rep.env[(0, i)]) != 0:
                    actions.append(self.generate_action((0, i)))
        else:
            for i in range(1, 7):
                if len(self.rep.env[(1, i - 1)]) != 0:
                    actions.append(self.generate_action((1, i - 1)))
        return actions

    def generate_action(self, pool):
        """
        Generates an action from a pool.

        Args:
            pool (Tuple): The pool to play.

        Raises:
            ActionNotPermittedError: If the action is not permitted.

        Returns:
            Action: Generated action.
        """
        if len(self.rep.env[pool]) == 0:
            raise ActionNotPermittedError("Pool " + str(pool) + " is empty")
        env = self.rep.copy().get_env()
        player = self.get_next_player().get_id()
        pieces = len(env[pool])
        env[pool] = []
        single_piece = Piece("rock", None)
        while pieces > 0:
            pool = self.get_next_pool(pool, player)
            env[pool].append(single_piece.copy())
            pieces -= 1
        # if stop on empty, win all the pieces in front
        if len(env[pool]) == 1:
            if pool[0] == 0 and pool[1] > 0 and player == 0:
                front = (1, pool[1] - 1)
                if len(env[front]) > 0:
                    env[(0, 0)] += env[front]
                    env[(0, 0)].append(single_piece.copy())
                    env[front] = []
                    env[pool] = []
            elif pool[0] == 1 and pool[1] < BOARD_SIZE and player == 1:
                front = (0, pool[1] + 1)
                if len(env[front]) > 0:
                    env[(1, 6)] += env[front]
                    env[(1, 6)].append(single_piece.copy())
                    env[front] = []
                    env[pool] = []
        # if one side is empty, win all the pieces in front
        player0_done = True
        player1_done = True
        for i in range(1, 7):
            if len(env[(0, i)]) != 0:
                player0_done = False
            if len(env[(1, i - 1)]) != 0:
                player1_done = False
        if player0_done:
            for i in range(1, 7):
                if len(env[(1, i - 1)]) > 0:
                    env[(1, 6)] += env[(1, i - 1)]
                    env[(1, i - 1)] = []
        if player1_done:
            for i in range(1, 7):
                if len(env[(0, i)]) > 0:
                    env[(0, 0)] += env[(0, i)]
                    env[(0, i)] = []

        new_gs = GameStateMancala(self.compute_scores(env), self.compute_next_player(self.get_next_player(), self.rep.get_env(), env), self.players, BoardMancala(env))

        return Action(self.copy(), new_gs)

    def get_next_pool(self, pool, player):
        """
        Gets the next pool to play.

        Args:
            pool (Tuple): The current pool being played.
            player (int): The player to play.

        Raises:
            Exception: If the pool is not valid.

        Returns:
            Tuple: The next pool to play.
        """
        if pool[0] == 0 and pool[1] > 0:
            next_pool = (0, pool[1] - 1)
        elif pool[0] == 0 and pool[1] == 0:
            next_pool = (1, 0)
        elif pool[0] == 1 and pool[1] < BOARD_SIZE:
            next_pool = (1, pool[1] + 1)
        elif pool[0] == 1 and pool[1] == BOARD_SIZE:
            next_pool = (0, 6)
        else:
            raise Exception("Pool " + str(pool) + " is not valid")
        if (player == 0 and next_pool == (1, 6)) or (player == 1 and next_pool == (0, 0)):
            next_pool = self.get_next_pool(next_pool, player)
        return next_pool

    def compute_scores(self, env):
        """
        Computes the scores of the game.

        Args:
            env (Dict): The next environment.

        Returns:
            Dict: The scores of the game.
        """
        scores = {self.players[0].get_id(): len(env[(0, 0)]), self.players[1].get_id(): len(env[(1, 6)])}
        return scores

    def replay(self, player: Player, current_rep: Representation, next_rep: Representation) -> bool:
        """
        Determines if the player can replay.

        Args:
            player (Player): The player.
            current_rep (Representation): The current representation of the game.
            next_rep (Representation): The next representation of the game.

        Returns:
            bool: True if the player can replay.
        """
        if player.get_id() == 0:
            for i in range(1, 7):
                if len(current_rep[(0, i)]) > len(next_rep[(0, i)]) and (len(current_rep[(0, i)]) - i) % 13 == 0:
                    return True
        else:
            for i in range(0, 6):
                if len(current_rep[(1, i)]) > len(next_rep[(1, i)]) and (len(current_rep[(1, i)]) - (6 - i)) % 13 == 0:
                    return True

    def compute_next_player(self, player: Player, current_rep: Representation = None, next_rep: Representation = None) -> Player:
        """
        Gets the next player. If the player can replay, returns the same player. Otherwise, returns the next player in the list.

        Args:
            player (Player): The current player.
            current_rep (Representation, optional): The current representation of the game. Defaults to None.
            next_rep (Representation, optional): The next representation of the game. Defaults to None.

        Returns:
            Player: The next player.
        """
        if self.replay(player, current_rep, next_rep):
            return player
        return self.get_next_player()

    def copy(self):
        return GameStateMancala(self.scores, self.next_player, self.players, self.rep.copy())

    def __hash__(self) -> int:
        return hash(frozenset([(hash(pos), hash(len(piece))) for pos, piece in self.rep.get_env().items()]))
