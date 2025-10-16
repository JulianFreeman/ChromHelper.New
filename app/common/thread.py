from typing import Callable
from PySide6.QtCore import Qt, QObject, QThread
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget
from qfluentwidgets import MessageBoxBase, BodyLabel


class TaskWorker(QThread):

    def __init__(
            self,
            parent: QObject,
            func: Callable,
            *args,
            **kwargs,
    ):
        super().__init__(parent)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.func(*self.args, **self.kwargs)


class BlockingDialog(MessageBoxBase):

    def __init__(self, msg: str, parent: QWidget = None):
        super().__init__(parent)
        self.viewLayout.addWidget(BodyLabel(msg, self))
        self.widget.setMinimumWidth(400)
        self.buttonGroup.hide()

    def keyPressEvent(self, event: QKeyEvent):
        # 强制关闭的方法，尽量不要用
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.close()
        else:
            super().keyPressEvent(event)


def run_some_task(msg: str, parent: QWidget, func: Callable, *args, **kwargs):
    worker = TaskWorker(parent, func, *args, **kwargs)
    bda = BlockingDialog(msg, parent)
    worker.finished.connect(bda.close)

    worker.start()
    # 堵塞，防止误触
    bda.exec()
