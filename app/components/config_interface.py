from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from qfluentwidgets import (
    CardWidget, IconWidget, BodyLabel, CaptionLabel, TransparentToolButton,
    setFont, ScrollArea, SmoothMode
)
from qfluentwidgets import FluentIcon as Fi
from app.common.utils import get_icon_path


class UserDataCard(CardWidget):

    def __init__(
            self,
            name: str,
            type_: str,
            exec_path: str,
            data_path: str,
            parent=None):
        super().__init__(parent)
        self.icon_widget = IconWidget(get_icon_path(type_), self)
        self.title_label = BodyLabel(name, self)
        setFont(self.title_label, 18)
        self.exec_label = CaptionLabel(exec_path, self)
        self.data_label = CaptionLabel(data_path, self)
        self.close_button = TransparentToolButton(Fi.CLOSE, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(90)
        self.icon_widget.setFixedSize(72, 72)

        self.hBoxLayout.setContentsMargins(15, 11, 11, 11)
        self.hBoxLayout.setSpacing(6)
        self.hBoxLayout.addWidget(self.icon_widget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(6)
        self.vBoxLayout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.exec_label, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.data_label, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignRight)

        self.close_button.setFixedSize(48, 48)
        # self.moreButton.clicked.connect(self.onMoreButtonClicked)


class ConfigInterface(ScrollArea):

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))

        userdata_info = [
            ["Chrome", "chrome",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Users\Julian\AppData\Local\Google\Chrome\User Data"],
            ["Edge", "edge",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Users\Julian\AppData\Local\Microsoft\Edge\User Data"],
            ["Brave", "brave",
             r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
             r"C:\Users\Julian\AppData\Local\BraveSoftware\Brave-Browser\User Data"],
            ["邮箱汇总", "chrome",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"F:/Chrome/GoogleEmails/User Data"],
            ["Chrome", "chrome",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Users\Julian\AppData\Local\Google\Chrome\User Data"],
            ["Edge", "edge",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Users\Julian\AppData\Local\Microsoft\Edge\User Data"],
            ["Brave", "brave",
             r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
             r"C:\Users\Julian\AppData\Local\BraveSoftware\Brave-Browser\User Data"],
            ["邮箱汇总", "chrome",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"F:/Chrome/GoogleEmails/User Data"],
        ]

        self.cw = QWidget(self)
        self.setWidget(self.cw)

        self.vly_wg = QVBoxLayout()
        self.cw.setLayout(self.vly_wg)

        self.vly_wg.setSpacing(6)
        self.vly_wg.setAlignment(Qt.AlignmentFlag.AlignTop)

        for name, type_, exec_path, data_path in userdata_info:
            self.add_card(name, type_, exec_path, data_path)

        self.enableTransparentBackground()
        self.setWidgetResizable(True)
        # self.setSmoothMode(SmoothMode.NO_SMOOTH, Qt.Orientation.Vertical)
        # self.setSmoothMode(SmoothMode.NO_SMOOTH, Qt.Orientation.Horizontal)

    def add_card(self, name: str, type_: str, exec_path: str, data_path: str):
        card = UserDataCard(name, type_, exec_path, data_path, self)
        self.vly_wg.addWidget(card, alignment=Qt.AlignmentFlag.AlignTop)
