from typing import Callable
from PySide6.QtCore import Qt, QObject, QSize, QThread
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget


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


class BlockingDialog(QDialog):

    def __init__(self, title: str, msg: str, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle(title)

        # 设置没有关闭按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        # 布局和内容
        layout = QVBoxLayout()
        layout.addWidget(QLabel(msg, self))
        self.setLayout(layout)

    def sizeHint(self):
        return QSize(200, 50)

    def keyPressEvent(self, event: QKeyEvent):
        # 强制关闭的方法，尽量不要用
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.close()
        else:
            super().keyPressEvent(event)


def run_some_task(title: str, msg: str, parent: QWidget, func: Callable, *args, **kwargs):
    worker = TaskWorker(parent, func, *args, **kwargs)
    bda = BlockingDialog(title, msg, parent)
    worker.finished.connect(bda.close)

    worker.start()
    # 堵塞，防止误触
    bda.exec()
