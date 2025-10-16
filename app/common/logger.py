import sys
from logging import Logger
from types import TracebackType
from typing import Type


class FakeLogger(object):
    """当没有提供 Logger 时占位用的"""

    def debug(self, msg: str):
        pass

    def info(self, msg: str):
        pass

    def warning(self, msg: str):
        pass

    def error(self, msg: str):
        pass

    def critical(self, msg: str):
        pass


def get_excepthook_for(logger: Logger):

    def my_excepthook(
            exc_type: Type[BaseException],
            exc_value: BaseException,
            exc_traceback: TracebackType | None,
    ):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.error("Found exception", exc_info=(exc_type, exc_value, exc_traceback))

    return my_excepthook
