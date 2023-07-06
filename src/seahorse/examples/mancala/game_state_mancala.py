from __future__ import annotations

from seahorse.examples.mancala.board_mancala import BoardMancala
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player
from seahorse.utils.custom_exceptions import ActionNotPermittedError

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

    def __init__(self, scores: dict, next_player: Player, players: list[Player], rep: BoardMancala) -> None:
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
        for i in range(1,7):
            if self.rep.env[(0,i)].get_value() != 0:
                player1_done = False
            if self.rep.env[(1,i-1)].get_value() != 0:
                player2_done = False
        return player1_done or player2_done

    def generate_possible_actions(self) -> set[Action]:
        """
        Generates all possible actions from the current game state.

        Raises:
            ActionNotPermittedError: If the action is not permitted.

        Returns:
            Set[Action]: Set of possible actions.
        """
        next_player = self.get_next_player().get_id()
        actions = set()
        if next_player == self.players[0].get_id():
            for i in range(1,7):
                if self.rep.env[(0,i)].get_value() != 0:
                    actions.add(self.generate_action((0,i)))
        else:
            for i in range(1,7):
                if self.rep.env[(1,i-1)].get_value() != 0:
                    actions.add(self.generate_action((1,i-1)))
        return actions

    def generate_action(self, pool) -> Action:
        """
        Generates an action from a pool.

        Args:
            pool (Tuple): The pool to play.

        Raises:
            ActionNotPermittedError: If the action is not permitted.

        Returns:
            Action: Generated action.
        """
        if self.rep.env[pool].get_value() == 0:
            raise ActionNotPermittedError("Pool "+str(pool)+" is empty")
        env = self.rep.copy().get_env()
        player = self.get_next_player().get_id()
        pieces = env[pool].remove()
        while pieces > 0:
            pool = self.get_next_pool(pool,player)
            env[pool].increment()
            pieces -= 1
        # if stop on empty, win all the pieces in front
        if env[pool].get_value() == 1:
            if pool[0] == 0 and pool[1] > 0 and player == 0:
                front = (1, pool[1] - 1)
                if len(env[front]) > 0:
                    env[(0,0)].increment(env[front].remove())
                    env[(0,0)].increment(env[pool].remove())
            elif pool[0] == 1 and pool[1] < BOARD_SIZE and player == 1:
                front = (0,pool[1]+1)
                if env[front].get_value() > 0:
                    env[(1,6)].increment(env[front].remove())
                    env[(1,6)].increment(env[pool].remove())
        # if one side is empty, win all the pieces in front
        player0_done = True
        player1_done = True
        for i in range(1,7):
            if env[(0,i)].get_value() != 0:
                player0_done = False
            if env[(1,i-1)].get_value() != 0:
                player1_done = False
        if player0_done:
            for i in range(1,7):
                if env[(1,i-1)].get_value() > 0:
                    env[(1,6)].increment(env[(1,i-1)].remove())
        if player1_done:
            for i in range(1,7):
                if env[(0,i)].get_value() > 0:
                    env[(0,0)].increment(env[(0,i)].remove())

        new_gs = GameStateMancala(self.compute_scores(env), self.compute_next_player(self.get_next_player(), self.rep.get_env(), env), self.players, BoardMancala(env))

        return Action(self.copy(), new_gs)

    def get_next_pool(self, pool, player) -> tuple[int, int]:
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

    def compute_scores(self, env) -> dict[int, float]:
        """
        Computes the scores of the game.

        Args:
            env (Dict): The next environment.

        Returns:
            Dict: The scores of the game.
        """
        scores = {self.players[0].get_id():env[(0,0)].get_value(), self.players[1].get_id():env[(1,6)].get_value()}
        return scores

    def replay(self, player: Player, current_rep: dict, next_rep: dict) -> bool:
        """
        Determines if the player can replay.

        Args:
            player (Player): The player.
            current_rep (Representation): The current representation of the game.
            next_rep (Representation): The next representation of the game.

        Returns:
            bool: True if the player can replay.
        """
        if player.get_id() == self.players[0].get_id():
            for i in range(1,7):
                if current_rep[(0,i)].get_value() > next_rep[(0,i)].get_value() and (current_rep[(0,i)].get_value() - i)%13 == 0:
                    return True
        else:
            for i in range(0,6):
                if current_rep[(1,i)].get_value() > next_rep[(1,i)].get_value() and (current_rep[(1,i)].get_value() - (6-i))%13 == 0:
                    return True
        return False

    def compute_next_player(self, player: Player, current_rep: dict = None, next_rep: dict = None) -> Player:
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
        return super().compute_next_player()

    def copy(self) -> GameStateMancala:
        return GameStateMancala(self.scores, self.next_player, self.players, self.rep.copy())

    def __hash__(self) -> int:
        return hash(frozenset([(hash(pos),hash(piece.get_value())) for pos,piece in self.rep.get_env().items()]))
