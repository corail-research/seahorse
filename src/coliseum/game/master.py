from abc import abstractmethod
from coliseum.game.game_state import GameState
from coliseum.utils.custom_exceptions import MethodNotImplementedError


class Master:
    """
    Attributes:
        name (str): name of the instance
        game_state (GameState): state of the game
        log_file (str): name of the log file
    """

    def __init__(self,
                 name: str,
                 game_state: GameState,
                 log_file: str
                 ) -> None:
        self.name = name
        self.game_state = game_state
        self.log_file = log_file

    @abstractmethod
    def play(self):
        raise MethodNotImplementedError()

    @abstractmethod
    def update_json(self):
        raise MethodNotImplementedError()

    def get_name(self):
        """
        Returns:
            str: name
        """
        return self.name

    def get_game_state(self):
        """
        Returns:
            GameState: game_state
        """
        return self.game_state

    def get_json_path(self):
        """
        Returns:
            str: log_file
        """
        return self.log_file

    @abstractmethod
    def update_game_state(self):
        raise MethodNotImplementedError()
