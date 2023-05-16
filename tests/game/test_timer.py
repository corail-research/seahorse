from coliseum.game.time_manager import TimeMixin
import time
import unittest

from coliseum.utils.custom_exceptions import AlreadyRunningError, ColiseumTimeoutError, NotRunningError, TimerNotInitializedError


class DummyClass(TimeMixin):
    def __init__(self):
        self.dummy_attr = "bob"


class MixinTestCase(unittest.TestCase):

    def test_time_mixin_init_object(self):
        dummy = DummyClass()
        assert dummy.dummy_attr == "bob"

    def test_time_mixin_not_initialized(self):
        dummy = DummyClass()
        self.assertRaises(TimerNotInitializedError, dummy.start_timer)

    def test_time_mixin_init_timer(self):
        dummy = DummyClass()
        dummy.init_timer(10)
        assert dummy.get_time_limit() == 10
        assert dummy.get_remaining_time() == 10
        assert dummy._is_initialized
        assert not dummy.is_locked()
        assert not dummy.is_running()

    def test_time_mixin_start_twice(self):
        dummy = DummyClass()
        dummy.init_timer(10)
        dummy.start_timer()
        self.assertRaises(AlreadyRunningError, dummy.start_timer)

    def test_time_mixin_stop_twice(self):
        dummy = DummyClass()
        dummy.init_timer(10)
        dummy.start_timer()
        dummy.stop_timer()
        self.assertRaises(NotRunningError, dummy.stop_timer)

    def test_time_lock(self):
        dummy = DummyClass()
        dummy.init_timer(.5)
        dummy.start_timer()

        time.sleep(.1)
        dummy.dummy_attr = "marcel"
        time.sleep(.4)

        def change_attr():
            dummy.dummy_attr = "bob"

        self.assertRaises(ColiseumTimeoutError, change_attr)
        assert dummy.is_locked()
