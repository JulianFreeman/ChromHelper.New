import sys
import logging
from PySide6.QtWidgets import QApplication
from app.common import resources
from app.common.logger import get_excepthook_for
from app.components.main_window import MainWindow

__version__ = '4.0.0'
ORG_NAME = "Oranje"
APP_NAME = "ChromHelper"
ZH_APP_NAME = "浏览器助手"


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    sys.excepthook = get_excepthook_for(logger)

    win = MainWindow(logger)
    win.setWindowTitle(f"{ZH_APP_NAME} {__version__}")
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
