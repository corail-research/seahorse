import functools
import inspect
import logging


def _logger_caller(fun):
    """
    Internal decorator to get the caller class name

    Args:
        fun (String): a logging function

    Returns:
        void :
    """
    @functools.wraps(fun)
    def wrapper(self, *args, **kwargs):
        caller_class = inspect.currentframe().f_back.f_locals.get("self").__class__.__name__
        kwargs["caller"] = caller_class
        return fun(self, *args, **kwargs)


    return wrapper


class Logger:
    """Custom Logger

    Attributes:
        logger (Logger): logger instance

    """
    def __init__(self):
        """
        Constructor for the logger, adds VERBOSE level and a custom formatter

        Returns:
            void :

        """
        self.logger = logging.getLogger("Logger")
        self.logger.setLevel(logging.DEBUG)

        # Custom log levels
        logging.addLevelName(logging.DEBUG + 5, "VERBOSE")
        logging.VERBOSE = logging.DEBUG + 5


        formatter = logging.Formatter("[%(levelname)s][%(asctime)s][%(caller)s] %(message)s")

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)


        console_handler.setFormatter(logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(caller)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))


    @_logger_caller
    def debug(self, message, **kwargs):
        """debug logging

        Args:
            message (String): message to log
        """
        caller = kwargs.get("caller", "")
        extra = {"caller": caller}
        self.logger.debug(message, extra=extra)

    @_logger_caller
    def verbose(self, message, **kwargs):
        """verbose logging

        Args:
            message (String): message to log
        """
        caller = kwargs.get("caller", "")
        extra = {"caller": caller}
        self.logger.log(logging.VERBOSE, message, extra=extra)

    @_logger_caller
    def info(self, message, **kwargs):
        """info logging

        Args:
            message (String): message to log
        """
        caller = kwargs.get("caller", "")
        extra = {"caller": caller}
        self.logger.info(message, extra=extra)

    @_logger_caller
    def warning(self, message, **kwargs):
        """warning logging

        Args:
            message (String): message to log
        """
        caller = kwargs.get("caller", "")
        extra = {"caller": caller}
        self.logger.warning(message, extra=extra)

    @_logger_caller
    def error(self, message, **kwargs):
        """error logging

        Args:
            message (String): message to log
        """
        caller = kwargs.get("caller", "")
        extra = {"caller": caller}
        self.logger.error(message, extra=extra)

    @_logger_caller
    def critical(self, message, **kwargs):
        """critical error logging

        Args:
            message (String): message to log
        """
        caller = kwargs.get("caller", "")
        extra = {"caller": caller}
        self.logger.critical(message, extra=extra)
