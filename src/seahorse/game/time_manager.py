import functools
import time
from typing import Any

from seahorse.utils.custom_exceptions import (
    AlreadyRunningError,
    ColiseumTimeoutError,
    NotRunningError,
    TimerNotInitializedError,
)


def _timer_init_safeguard(fun):
    """
    Interal decorator to prevent calling timer methods before
    its inialization.

    Args:
        fun (_type_): _description_

    Raises:
        TimerNotInitializedError: _description_

    Returns:
        _type_: _description_
    """
    @functools.wraps(fun)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_is_initialized"):
            raise TimerNotInitializedError()
        else:
            return fun(self, *args, **kwargs)

    return wrapper

class TimeMixin:
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

    def init_timer(self, time_limit: int) -> None:
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

    @_timer_init_safeguard
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

    @_timer_init_safeguard
    def is_running(self) -> bool:
        """
        Is the timer running ?

        Returns:
            bool: `True` if the timer is running, `False` otherwise
        """
        return self._is_running

    @_timer_init_safeguard
    def get_time_limit(self):
        """
        Get the limit set in `set_time_limit()`
        """
        return self._time_limit

    @_timer_init_safeguard
    def get_remaining_time(self) -> float:
        """Gets the timer's remaining time

        Returns:
            float: the remaining time
        """
        if self._is_running:
            return self._remaining_time - (time.time() - self._last_timestamp)
        else:
            return self._remaining_time

    @_timer_init_safeguard
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

    @_timer_init_safeguard
    def is_locked(self) -> bool:
        """Is the time credit expired ?

        Returns:
            bool: `True` if expired `False` otherwise
        """
        print("time :", self.get_remaining_time())
        return self.get_remaining_time() <= 0

    def __setattr__(self, __name: str, value: Any) -> None:
        """_summary_

        Args:
            Inherited from object
        Raises:
            TimeoutException: prevents modification after timout

        """
        try:
            if self.is_locked():
                raise ColiseumTimeoutError()
            else:
                self.__dict__[__name] = value

        except TimerNotInitializedError:
            self.__dict__[__name] = value
        except Exception as e:
            raise e

def timed_function(fun):
    """
    Decorator to prevent using a function after object's timeout.
    Args:
        fun (_type_): wrapped function

    Raises:
        TimerNotInitializedError: _description_
        Exception: _description_
        ColiseumTimeoutError: _description_

    Returns:
        Callable[...]: wrapper
    """
    @functools.wraps(fun)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_is_initialized"):
            raise TimerNotInitializedError()
        if not hasattr(self,"get_time_limit"):
            msg = "Using @timed_func within a object that is not timed.\n Please use TimeMixin."
            raise Exception(msg)
        elif(self.is_locked()):
            raise ColiseumTimeoutError()
        return fun(self, *args, **kwargs)
    return wrapper
