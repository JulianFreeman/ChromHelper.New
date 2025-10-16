# coding: utf8
from logging import (
    Logger, Handler, LogRecord,
    Formatter,
)
from qfluentwidgets import TextEdit

DEBUG_OUTPUT_CACHE = []


class TextEditHandler(Handler):

    def __init__(self, txe_wg: TextEdit, level: int | str = 0):
        super().__init__(level=level)
        self.txe_wg = txe_wg

    def emit(self, record: LogRecord):
        msg = self.format(record)
        self.txe_wg.append(msg)
        self.txe_wg.moveCursor(self.txe_wg.textCursor().MoveOperation.End)


class DebugInterface(TextEdit):

    def __init__(self, name: str, logger: Logger, parent=None):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))
        self.logger = logger
        self.formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")

        self.load_previous_output()

        self.txe_handler = TextEditHandler(self, self.logger.level)
        self.txe_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.txe_handler)


    def load_previous_output(self):
        """将之前缓存的输出加载到 TextEdit 中"""
        for text in DEBUG_OUTPUT_CACHE:
            self.append(text)
        self.moveCursor(self.textCursor().MoveOperation.End)
