class AlreadyRunningError(Exception):
    """Thrown when trying to start somethin twice
    """

    def __init__(self,  message: str = "Trying to start something twice !"):
        self.message = message
        super().__init__(message)


class NotRunningError(Exception):
    """Thrown when trying to stop somethin twice
    """

    def __init__(self,  message: str = "Trying to stop something twice !"):
        self.message = message
        super().__init__(message)

class NoGameStateProvidedError(Exception):
    """Thrown when trying to get a heavy action from a light action without providing a game state
    """
    def __init__(self,  message: str = "Cannot apply a light action without current game state."):
        self.message = message
        super().__init__(message)
class PlayerDuplicateError(Exception):
    """Thrown when trying to stop somethin twice
    """

    def __init__(self,  message: str = "Duplicates in the players list."):
        self.message = message
        super().__init__(message)


class SeahorseTimeoutError(Exception):
    """Thrown when trying to modify an expired element
    """

    def __init__(self,  message: str = "Trying to modify an expired element ! Time is out !"):
        self.message = message
        super().__init__(message)


class TimerNotInitializedError(Exception):
    """Thrown when trying to use timer utilities before timer initialization
    """

    def __init__(self,  message: str = "Timer not initialized."):
        self.message = message
        super().__init__(message)


class MethodNotImplementedError(Exception):
    """Thrown when trying to use a method not implemented
    """

    def __init__(self,  message: str = "Method not implemented."):
        self.message = message
        super().__init__(message)


class ActionNotPermittedError(Exception):
    """Thrown when trying to generate an action that's not permitted
    """

    def __init__(self,  message: str = "Action not permitted"):
        self.message = message
        super().__init__(message)

class StopAndStartError(Exception):
    """Thrown when trying to generate an action that's not permitted
    """

    def __init__(self,  message: str = "Timer was tampered with and exceeded the tolerancy set in GameMaster."):
        self.message = message
        super().__init__(message)

class ConnectionProblemError(Exception):
    """Thrown when trying to generate an action that's not permitted
    """

    def __init__(self,  message: str = "Connection problem"):
        self.message = message
        super().__init__(message)


class NoTournamentFailError(Exception):
    """Thrown when trying to generate an action that's not permitted
    """

    def __init__(self,  message: str = "Tournament problem : tournament is none, please connect to an existing tournament or create a tournament"):
        self.message = message
        super().__init__(message)
