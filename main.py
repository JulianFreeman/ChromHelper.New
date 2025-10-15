import sys
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QWidget, QVBoxLayout
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QModelIndex, QAbstractListModel, QSize
from qfluentwidgets import (
    MSFluentWindow, SubtitleLabel, setFont, NavigationItemPosition,
    PushButton, MessageBox, ModelComboBox, setTheme, Theme, MSFluentTitleBar
)
from qfluentwidgets import FluentIcon as Fi
from app.common import resources
from app.components.profiles_table import ProfilesTable
from app.components.extensions_table import ExtensionsTable
from app.components.bookmarks_table import BookmarksTable
from app.components.config_interface import ConfigInterface
from app.chromy import ChromInstance
from app.common.thread import run_some_task
from app.common.utils import get_icon_path
from app.common.logger import FakeLogger


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class UserDataListModel(QAbstractListModel):

    def __init__(
            self,
            userdata_info: list[list[str]],  # [[name, type, exec, data]]
            parent: QWidget = None,
    ):
        super().__init__(parent)
        self.userdata_info = userdata_info

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.userdata_info)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        if role == Qt.ItemDataRole.EditRole:
            return self.userdata_info[row][0]
        if role == Qt.ItemDataRole.DecorationRole:
            return QIcon(get_icon_path(self.userdata_info[row][1]))
        if role == Qt.ItemDataRole.UserRole:
            return self.userdata_info[row][1], self.userdata_info[row][2], self.userdata_info[row][3]
        return None

    def update_model(self, userdata_info: list[list[str]]):
        self.beginResetModel()
        self.userdata_info = userdata_info
        self.endResetModel()


class CHMSFluentWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.vly_right = QVBoxLayout()

        self.wg_top = QWidget(self)
        self.hly_top = QHBoxLayout()
        # self.vly_right.addLayout(self.hly_top)
        self.wg_top.setLayout(self.hly_top)
        self.hly_top.setContentsMargins(0, 0, 0, 0)

        self.pbn_refresh = PushButton(self)
        self.pbn_refresh.setText("刷新当前数据")
        self.pbn_refresh.setIcon(Fi.UPDATE)
        self.pbn_refresh.setMinimumWidth(100)

        self.cmbx_browsers = ModelComboBox(self)
        self.cmbx_browsers.setMinimumWidth(150)

        self.hly_top.addWidget(self.cmbx_browsers)
        self.hly_top.addWidget(self.pbn_refresh)
        self.hly_top.addStretch(1)
        self.hly_top.setSpacing(4)

        self.vly_right.addWidget(self.wg_top)
        self.vly_right.addWidget(self.stackedWidget)
        self.vly_right.setSpacing(2)
        self.hBoxLayout.addLayout(self.vly_right, stretch=1)

    def switchTo(self, interface: QWidget):
        super().switchTo(interface)
        if interface.property("is_bottom"):
            self.wg_top.setHidden(True)
        else:
            self.wg_top.setHidden(False)


class MainWindow(CHMSFluentWindow):

    def __init__(self):
        super().__init__()
        self.logger = FakeLogger()
        self.chrom_ins_map: dict[str, ChromInstance] = {}
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
             r"F:/Chrome/GoogleEmails/User Data"]
        ]
        self.userdata_model = UserDataListModel(userdata_info, self)
        self.cmbx_browsers.setModel(self.userdata_model)
        self.init_window()

        self.profile_interface = ProfilesTable(name='profile', parent=self)
        self.extension_interface = ExtensionsTable(name='extension', parent=self)
        self.bookmark_interface = BookmarksTable(name='bookmark', parent=self)
        self.config_interface = ConfigInterface(name="config", parent=self)
        self.config_interface.setProperty("is_bottom", True)
        self.settings_interface = Widget("settings", parent=self)
        self.settings_interface.setProperty("is_bottom", True)
        self.debug_interface = Widget("debug", parent=self)
        self.debug_interface.setProperty("is_bottom", True)

        self.addSubInterface(self.profile_interface, get_icon_path("profile"), "用户")
        self.addSubInterface(self.extension_interface, get_icon_path("extension"), "插件")
        self.addSubInterface(self.bookmark_interface, get_icon_path("bookmark"), "书签")
        self.addSubInterface(self.config_interface, get_icon_path("config"), "配置", position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.debug_interface, get_icon_path("debug"), "输出", position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settings_interface, get_icon_path("settings"), "设置", position=NavigationItemPosition.BOTTOM)

        self.pbn_refresh.clicked.connect(self.on_pbn_refresh_clicked)
        self.cmbx_browsers.currentIndexChanged.connect(self.on_cmbx_browsers_current_index_changed)

        if self.userdata_model.rowCount() > 0:
            self.cmbx_browsers.setCurrentIndex(0)

    def init_window(self):
        setTheme(Theme.LIGHT)
        self.resize(1000, 760)
        self.setWindowIcon(QIcon(":/images/logo.png"))
        self.setWindowTitle("浏览器助手")
        desktop = QApplication.screens()[0].availableGeometry()
        width, height = desktop.width(), desktop.height()
        self.move(width // 2 - self.width() // 2, height // 2 - self.height() // 2)

    def update_all_data(self, chrom_ins: ChromInstance, browser: str, exec_path: str):
        self.profile_interface.update_model(
            browser,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
        )
        self.extension_interface.update_model(
            chrom_ins.extensions,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
            chrom_ins.delete_extensions,
        )
        self.bookmark_interface.update_model(
            chrom_ins.bookmarks,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
            chrom_ins.delete_bookmarks,
        )

    def _update_chrom_ins_map(self, name: str, data_path: str):
        # 这个函数不涉及 UI 操作，避免在子线程运行时出问题
        chrom_ins = ChromInstance(data_path, self.logger)
        chrom_ins.fetch_all_profiles()
        chrom_ins.fetch_extensions_from_all_profiles()
        chrom_ins.fetch_bookmarks_from_all_profiles()
        self.chrom_ins_map[name] = chrom_ins

    def update_by_one_index(self, index: QModelIndex, force: bool):
        name = index.data(Qt.ItemDataRole.EditRole)
        type_, exec_path, data_path = index.data(Qt.ItemDataRole.UserRole)
        if force or name not in self.chrom_ins_map:
            self._update_chrom_ins_map(name, data_path)
        self.update_all_data(self.chrom_ins_map[name], type_, exec_path)

    def on_pbn_refresh_clicked(self):
        index = self.cmbx_browsers.model().createIndex(self.cmbx_browsers.currentIndex(), 1)
        self.update_by_one_index(index, force=True)

    def on_cmbx_browsers_current_index_changed(self, index: int):
        index = self.cmbx_browsers.model().createIndex(index, 1)
        self.update_by_one_index(index, force=False)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
