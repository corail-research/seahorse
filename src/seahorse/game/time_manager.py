import builtins
import functools
import time
from typing import Any

from loguru import logger

from seahorse.utils.custom_exceptions import (
    AlreadyRunningError,
    NotRunningError,
    SeahorseTimeoutError,
    TimerNotInitializedError,
)


class TimeMaster:
    __instance = None

    class Timer:
        def __init__(self,time_limit:float=1e9):
            self._time_limit = time_limit
            self._remaining_time = time_limit
            self._last_timestamp = None
            self._is_running = False

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

        def get_last_timestamp(self):
            """
            Get the last timestamp set at start_timer()
            """
            return self._last_timestamp

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


        def is_locked(self) -> bool:
            """Is the time credit expired ?

            Returns:
                bool: `True` if expired `False` otherwise
            """
            logger.info(f"time : {self.get_remaining_time()}")
            return self.get_remaining_time() <= 0

    @staticmethod
    def get_instance()->"TimeMaster":
        if TimeMaster.__instance is None:
            TimeMaster.__instance=TimeMaster()
        return TimeMaster.__instance

    @classmethod
    def register_timer(cls: "TimeMaster", linked_instance: Any, time_limit:float=1e9):
        pid = linked_instance.__dict__.get("id",builtins.id(linked_instance))
        cls.get_instance().__time_register[pid]=cls.get_instance().__time_register.get(pid,TimeMaster.Timer(time_limit))

    @classmethod
    def get_timer(cls: "TimeMaster", linked_instance: Any)-> Timer:
        return cls.get_instance().__time_register.get(linked_instance.__dict__.get("id",builtins.id(linked_instance)))


    def __init__(self):
        if TimeMaster.__instance is not None:
            msg = "Trying to initialize multiple instances of TimeMaster, this is forbidden to avoid side-effects.\n Call TimeMaster.get_instance() instead."
            raise NotImplementedError(msg)
        else:
            self.__time_register={}

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
            x.myattr=5  # raises SeahorseTimeoutException

    ```
    """

    def init_timer(self, time_limit: int) -> None:
        """
        Initializes the time credit of the instance

        Doesn't start the timer yet ! Call `start_timer()`.

        Args:
            time_limit (int): max time before locking all methods of the class
        """
        TimeMaster.register_timer(self,time_limit)

    def start_timer(self) -> float:
        """Starts the timer

        Raises:
            AlreadyRunningException: when trying to start twice.
        """
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        return TimeMaster.get_timer(self).start_timer()

    def is_running(self) -> bool:
        """
        Is the timer running ?

        Returns:
            bool: `True` if the timer is running, `False` otherwise
        """
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        return TimeMaster.get_timer(self).is_running()

    def get_time_limit(self):
        """
        Get the limit set in `set_time_limit()`
        """
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        return TimeMaster.get_timer(self).get_time_limit()

    def get_remaining_time(self) -> float:
        """Gets the timer's remaining time

        Returns:
            float: the remaining time
        """
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        return TimeMaster.get_timer(self).get_remaining_time()

    def get_last_timestamp(self) -> float:
        """Gets the timer's last recorded timestamp at which it was started

        Returns:
            float: the timestamp
        """
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        return TimeMaster.get_timer(self).get_last_timestamp()

    def stop_timer(self) -> float:
        """Pauses the timer

        Raises:
            NotRunningException: when the timer isn't running

        Returns:
            float: remaining time
        """
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        return TimeMaster.get_timer(self).stop_timer()


    def is_locked(self) -> bool:
        """Is the time credit expired ?

        Returns:
            bool: `True` if expired `False` otherwise
        """
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        return TimeMaster.get_timer(self).is_locked()

    def __setattr__(self, __name: str, value: Any) -> None:
        """_summary_

        Args:
            Inherited from object
        Raises:
            TimeoutException: prevents modification after timout

        """
        try:
            if TimeMaster.get_timer(self) and self.is_locked():
                raise SeahorseTimeoutError()
            else:
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
        SeahorseTimeoutError: _description_

    Returns:
        Callable[...]: wrapper
    """
    @functools.wraps(fun)
    def wrapper(self, *args, **kwargs):
        r = fun(self, *args, **kwargs)
        if TimeMaster.get_timer(self) is None:
            raise TimerNotInitializedError
        elif(self.is_locked()):
            raise SeahorseTimeoutError()
        return r
    return wrapper
