import time
import unittest

from seahorse.game.time_manager import TimeMixin, timed_function
from seahorse.utils.custom_exceptions import (
    AlreadyRunningError,
    NotRunningError,
    SeahorseTimeoutError,
    TimerNotInitializedError,
)


class DummyClass(TimeMixin):
    def __init__(self):
        self.dummy_attr = "bob"

    @timed_function
    def only_before_timeout(self):
        return True


class MixinTestCase(unittest.TestCase):

    def setUp(self):
        self.dummy = DummyClass()

    def test_time_mixin_init_object(self):
        assert self.dummy.dummy_attr == "bob"

    def test_timer_not_init(self):
        self.assertRaises(TimerNotInitializedError, self.dummy.get_time_limit)
        self.assertRaises(TimerNotInitializedError, self.dummy.get_remaining_time)
        self.assertRaises(TimerNotInitializedError, self.dummy.start_timer)
        self.assertRaises(TimerNotInitializedError, self.dummy.stop_timer)
        self.assertRaises(TimerNotInitializedError, self.dummy.is_locked)
        self.assertRaises(TimerNotInitializedError, self.dummy.is_running)
        self.assertRaises(TimerNotInitializedError, self.dummy.get_last_timestamp)
    
    def test_time_mixin_init_timer(self):
        self.dummy.init_timer(10)
        assert self.dummy.get_time_limit() == 10
        assert self.dummy.get_remaining_time() == 10
        assert not self.dummy.is_locked()
        assert not self.dummy.is_running()

    def test_time_mixin_start_twice(self):
        self.dummy.init_timer(10)
        self.dummy.start_timer()
        self.assertRaises(AlreadyRunningError, self.dummy.start_timer)

    def test_time_mixin_stop_twice(self):
        self.dummy.init_timer(10)
        self.dummy.start_timer()
        self.dummy.stop_timer()
        self.assertRaises(NotRunningError, self.dummy.stop_timer)

    def test_time_lock(self):

        def change_attr():
            self.dummy.dummy_attr = "bob"

        def call_blocked_method():
            return self.dummy.only_before_timeout()

        self.dummy.init_timer(.5)
        self.dummy.start_timer()

        time.sleep(.1)
        self.dummy.dummy_attr = "marcel"
        assert call_blocked_method()
        time.sleep(.4)

        self.assertRaises(SeahorseTimeoutError, change_attr)
        self.assertRaises(SeahorseTimeoutError, call_blocked_method)
        assert self.dummy.is_locked()

    def tearDown(self) -> None:
        self.dummy = None
