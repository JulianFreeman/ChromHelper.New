from logging import Logger
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QWidget, QVBoxLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QModelIndex, QAbstractListModel, QSize, QThread, Signal
from qfluentwidgets import (
    MSFluentWindow, NavigationItemPosition, PillPushButton,
    PushButton, ModelComboBox, setTheme, SplashScreen, SystemThemeListener,
    InfoBar, InfoBarPosition
)
from qfluentwidgets import FluentIcon as Fi
from app.components.profiles_table import ProfilesTable
from app.components.extensions_table import ExtensionsTable
from app.components.bookmarks_table import BookmarksTable
from app.components.config_interface import ConfigInterface
from app.components.debug_interface import DebugInterface
from app.components.settings_interface import SettingsInterface
from app.chromy import ChromInstance
from app.common.thread import run_some_task
from app.common.api_worker import ApiWorker
from app.common.utils import get_icon_path, SAFE_MAP_ICON, SafeMark
from app.common.config import cfg
from app.database.db_operations import DBManger


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
        self.wg_top.setLayout(self.hly_top)
        self.hly_top.setContentsMargins(0, 0, 5, 0)

        self.pbn_refresh = PushButton(self)
        self.pbn_refresh.setText("刷新当前数据")
        self.pbn_refresh.setIcon(Fi.UPDATE)
        self.pbn_refresh.setMinimumWidth(100)

        self.cmbx_browsers = ModelComboBox(self)
        self.cmbx_browsers.setMinimumWidth(150)

        self.hly_top.addWidget(self.cmbx_browsers)
        self.hly_top.addWidget(self.pbn_refresh)
        self.hly_top.addStretch(1)

        safe_checks = [
            ("安全", 1), ("未知", 0), ("不安全", -1), ("未记录", -2),
        ]
        self.switches_group = QWidget(self)
        self.hly_switches = QHBoxLayout()
        self.hly_switches.setContentsMargins(0, 0, 0, 0)
        self.switches_group.setLayout(self.hly_switches)
        self.safe_switches: list[PillPushButton] = []
        for text, m in safe_checks:
            c = PillPushButton(self.switches_group)
            c.setText(text)
            c.setIcon(SAFE_MAP_ICON[m])
            c.setProperty("mark", m)
            self.safe_switches.append(c)
            self.hly_switches.addWidget(c)

        self.hly_top.addWidget(self.switches_group)
        self.switches_group.hide()  # 一开始先隐藏
        self.hly_top.setSpacing(4)

        self.vly_right.addWidget(self.wg_top)
        self.vly_right.addWidget(self.stackedWidget)
        self.vly_right.setSpacing(2)
        self.hBoxLayout.addLayout(self.vly_right, stretch=1)

    def switchTo(self, interface: QWidget):
        super().switchTo(interface)
        self.wg_top.setHidden(interface.property("is_bottom") is True)
        self.switches_group.setHidden(interface.property("is_extension") is not True)


class MainWindow(CHMSFluentWindow):

    START_QUERY_EXT_SAFE_MARK= Signal()
    EXT_SAFE_MARK_PROCESS_FINISHED = Signal(dict)
    # 标记刚打开软件时的拉取数据
    IS_INIT = True

    def __init__(self, title: str, width: int, height: int, logger: Logger):
        super().__init__()
        self.logger = logger
        self.dbm = DBManger()
        self.chrom_ins_map: dict[str, ChromInstance] = {}
        self.ext_safe_marks: dict[str, SafeMark] = {}

        self.theme_listener = SystemThemeListener(self)

        userdata_info = self.dbm.select_all()
        self.userdata_model = UserDataListModel(userdata_info, self)
        self.cmbx_browsers.setModel(self.userdata_model)

        self.profile_interface = ProfilesTable(name='profile', parent=self)
        self.extension_interface = ExtensionsTable(name='extension', parent=self)
        self.bookmark_interface = BookmarksTable(name='bookmark', parent=self)
        self.config_interface = ConfigInterface(name="config", dbm=self.dbm, parent=self)
        self.debug_interface = DebugInterface(name="debug", logger=logger, parent=self)
        self.settings_interface = SettingsInterface(name="settings", parent=self)
        self.extension_interface.setProperty("is_extension", True)
        self.config_interface.setProperty("is_bottom", True)
        self.debug_interface.setProperty("is_bottom", True)
        self.settings_interface.setProperty("is_bottom", True)

        self.addSubInterface(self.profile_interface, get_icon_path("profile"), "用户")
        self.addSubInterface(self.extension_interface, get_icon_path("extension"), "插件")
        self.addSubInterface(self.bookmark_interface, get_icon_path("bookmark"), "书签")
        self.addSubInterface(self.config_interface, get_icon_path("config"), "配置", position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.debug_interface, get_icon_path("debug"), "输出", position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settings_interface, get_icon_path("settings"), "设置", position=NavigationItemPosition.BOTTOM)

        self.pbn_refresh.clicked.connect(self.on_pbn_refresh_clicked)
        self.cmbx_browsers.currentIndexChanged.connect(self.on_cmbx_browsers_current_index_changed)
        self.config_interface.userdata_changed.connect(self.on_config_userdata_changed)

        # === API Worker ===
        self.api_thread = QThread()
        self.worker = ApiWorker()
        self.worker.moveToThread(self.api_thread)
        self.worker.queryNecessaryFinished.connect(self.process_ext_safe_marks)
        self.worker.error.connect(self.handle_api_error)
        self.EXT_SAFE_MARK_PROCESS_FINISHED.connect(self.extension_interface.update_safe_marks)
        self.START_QUERY_EXT_SAFE_MARK.connect(self.worker.do_query_necessary)
        self.api_thread.start()

        # ===== prepare for splashscreen ======
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(":/images/logo.png"))
        self.resize_and_move_to_center(width, height)

        self.splash = SplashScreen(self.windowIcon(), self)
        self.splash.setIconSize(QSize(102, 102))
        # 必须要有这个
        self.show()

        # 如果电脑慢，可能会花点时间
        if self.userdata_model.rowCount() > 0:
            self.cmbx_browsers.setCurrentIndex(0)

        self.splash.finish()
        self.theme_listener.start()

        self.post_init_window(width, height)

        # 放最后
        for c in self.safe_switches:
            c.toggled.connect(self.update_filter)
            c.setChecked(True)

    def closeEvent(self, event):
        self.theme_listener.terminate()
        self.theme_listener.deleteLater()
        self.api_thread.quit()
        self.api_thread.wait()
        super().closeEvent(event)

    def post_init_window(self, width: int, height: int):
        setTheme(cfg.theme)
        self.setMicaEffectEnabled(False)
        self.stackedWidget.setAnimationEnabled(cfg.get(cfg.switch_animation))
        self.resize_and_move_to_center(width, height)

    def resize_and_move_to_center(self, width: int, height: int):
        self.resize(width, height)
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def process_ext_safe_marks(self, raw_ext_safe_marks: list[dict]):
        self.ext_safe_marks.clear()
        for e in raw_ext_safe_marks:
            self.ext_safe_marks[e["ID"]] = SafeMark(id=e["ID"], safe=e["SAFE"])
        self.EXT_SAFE_MARK_PROCESS_FINISHED.emit(self.ext_safe_marks)
        InfoBar.success("", "插件安全标记已更新", isClosable=True, duration=3000,
                        position=InfoBarPosition.BOTTOM_RIGHT, parent=self.window())

    def handle_api_error(self, error_message: str):
        """显示来自工作线程的错误消息"""
        InfoBar.error("", "无法获取插件安全标记", isClosable=True, duration=3000,
                      position=InfoBarPosition.BOTTOM_RIGHT, parent=self.window())
        self.logger.error(f"[API ERROR] {error_message}")

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
            self.ext_safe_marks,
        )
        self.bookmark_interface.update_model(
            chrom_ins.bookmarks,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
            chrom_ins.delete_bookmarks,
        )

    def _update_chrom_ins_map(self, name: str, data_path: str):
        # 这个函数不要涉及 UI 操作，避免在子线程运行时出问题
        chrom_ins = ChromInstance(data_path, self.logger)
        chrom_ins.fetch_all_profiles()
        chrom_ins.fetch_extensions_from_all_profiles()
        chrom_ins.fetch_bookmarks_from_all_profiles()
        self.chrom_ins_map[name] = chrom_ins

    def update_by_one_index(self, index: QModelIndex, force: bool):
        name = index.data(Qt.ItemDataRole.EditRole)
        type_, exec_path, data_path = index.data(Qt.ItemDataRole.UserRole)
        if force or self.IS_INIT:
            # 只在强制刷新的时候重新拉取一下标记
            # 不能直接调用 do_query_necessary，否则还是会堵塞窗口，要通过信号槽的方法
            self.START_QUERY_EXT_SAFE_MARK.emit()
            # 大部分时候拉取比较快，就不显示了
            # InfoBar.info("", "正在拉取插件安全标记……", isClosable=True, duration=3000,
            #              position=InfoBarPosition.BOTTOM_RIGHT, parent=self.window())
            self.IS_INIT = False

        if force or name not in self.chrom_ins_map:
            run_some_task("正在获取浏览器数据……", self,
                          self._update_chrom_ins_map, name=name, data_path=data_path)

        self.update_all_data(self.chrom_ins_map[name], type_, exec_path)

    def on_pbn_refresh_clicked(self):
        index = self.cmbx_browsers.model().createIndex(self.cmbx_browsers.currentIndex(), 1)
        self.update_by_one_index(index, force=True)

    def on_cmbx_browsers_current_index_changed(self, index: int):
        index = self.cmbx_browsers.model().createIndex(index, 1)
        self.update_by_one_index(index, force=False)

    def on_config_userdata_changed(self, is_reset: bool):
        self.userdata_model.update_model(self.dbm.select_all())
        if is_reset and self.userdata_model.rowCount() > 0:
            self.cmbx_browsers.setCurrentIndex(0)

    # 只有插件部分用到
    def update_filter(self, checked: bool):
        accepted_status = []
        for c in self.safe_switches:
            if c.isChecked():
                accepted_status.append(c.property("mark"))

        self.extension_interface.filter_model.set_accepted_status(accepted_status)
