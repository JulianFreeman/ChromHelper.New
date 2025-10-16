import sys
from PySide6.QtWidgets import QApplication
from app.common import resources

from app.components.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
