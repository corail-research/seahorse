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


class ColiseumTimeoutError(Exception):
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
