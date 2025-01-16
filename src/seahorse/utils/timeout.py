import signal
from seahorse.utils.custom_exceptions import SeahorseTimeoutError

# This timeout is not perfect
# limitation 1: precise timings
# - precision is at the second scale, no fractionnal value
# limitation 2: if a infinite loop/slow operation is in a non-python library (ex: numpy, or other c/rust based code):
# - python will process the signal after the non-python code is executed instead of closing early
# limitation 3: can be disabled by the player
# - the player can bypass it by removing the signal handler
class TimeOut:
    def __init__(self, seconds, timeout_callback= lambda : (), ex=SeahorseTimeoutError()):
        self.seconds = seconds
        self.timeout_callback = timeout_callback
        self.ex = ex
    def handle_timeout(self, *args, **kwargs):
        self.timeout_callback()
        raise self.ex
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, *args, **kwargs):
        signal.alarm(0)
