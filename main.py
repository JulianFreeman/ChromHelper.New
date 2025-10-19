import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale
from qfluentwidgets import FluentTranslator
from app.common import resources
from app.common.logger import get_excepthook_for
from app.components.main_window import MainWindow
from app.common.config import ORG_NAME, APP_NAME, ZH_APP_NAME, VERSION


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    translator = FluentTranslator(QLocale(QLocale.Language.Chinese, QLocale.Country.China))
    app.installTranslator(translator)

    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    sys.excepthook = get_excepthook_for(logger)

    win = MainWindow(title=f"{ZH_APP_NAME} {VERSION}",
                     width=1000,
                     height=760,
                     logger=logger)
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
