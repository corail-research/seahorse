import time

from seahorse.utils.custom_exceptions import (
    AlreadyRunningError,
    NotRunningError,
)


class Timer:
    """
    When implemented allows any object to keep track of time

    Example usage:
    ```
        import time
        class MyTimedObject(TimeMixin):
            def __init__(self):
                self.myattr = 2

            x = MyTimedObject()
            x.set_time_limit(10)
            x.start_timer()
            time.sleep(11)
            x.myattr=5  # raises ColiseumTimeoutException

    ```
    """

    def __init__(self, time_limit: float) -> None:
        """
        Initializes the time credit of the instance

        Doesn't start the timer yet ! Call `start_timer()`.

        Args:
            time_limit (int): max time before locking all methods of the class
        """
        self._time_limit = time_limit
        self._remaining_time = time_limit
        self._last_timestamp = None
        self._is_running = False

        self._is_initialized = True  # Must always be at the end

    def start_timer(self) -> float:
        """Starts the timer

        Raises:
            AlreadyRunningException: when trying to start twice.
        """
        if self._is_running:
            raise AlreadyRunningError()

        self._last_timestamp = time.time()

        self._is_running = True

        return self._last_timestamp

    def is_running(self) -> bool:
        """
        Is the timer running ?

        Returns:
            bool: `True` if the timer is running, `False` otherwise
        """
        return self._is_running

    def get_time_limit(self):
        """
        Get the limit set in `set_time_limit()`
        """
        return self._time_limit

    def get_remaining_time(self) -> float:
        """Gets the timer's remaining time

        Returns:
            float: the remaining time
        """
        if self._is_running:
            return self._remaining_time - (time.time() - self._last_timestamp)
        else:
            return self._remaining_time

    def stop_timer(self) -> float:
        """Pauses the timer

        Raises:
            NotRunningException: when the timer isn't running

        Returns:
            float: remaining time
        """
        if not self._is_running:
            raise NotRunningError()

        self._remaining_time = self._remaining_time - (time.time() - self._last_timestamp)

        self._is_running = False
        return self._remaining_time


    def is_finished(self) -> bool:
        """Is the time credit expired ?

        Returns:
            bool: `True` if expired `False` otherwise
        """
        return self.get_remaining_time() <= 0
