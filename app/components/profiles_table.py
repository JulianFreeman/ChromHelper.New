from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPoint, QSize, QAbstractListModel
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QTreeView, QWidget
from qfluentwidgets import TreeView, ModelComboBox, PushButton, RoundMenu, Action
from qfluentwidgets import FluentIcon as Fi

from app.chromy.structs import Profile
from app.chromy.chromi import (
    sort_profiles_id_func,
    ProfileSortFilterProxyModel,
    open_profiles,
    get_profile_picture,
)
from app.common.utils import show_quick_tip
# from .da_raw_data import DaRawData


class ProfilesModel(QAbstractTableModel):

    def __init__(self, browser: str, profiles: dict[str, Profile], parent=None):
        super().__init__(parent)
        self.browser = browser
        self.profiles = profiles
        self.profile_ids = list(profiles.keys())
        self.profile_ids.sort(key=sort_profiles_id_func)

        self.profile_pic_cache: dict[str, QIcon] = {}

        self.headers = ["ID", "名称", "邮箱"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.profile_ids)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        profile_id = self.profile_ids[index.row()]
        profile = self.profiles[profile_id]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            col_map = {
                0: profile.id,
                1: profile.name,
                2: profile.user_name,
            }
            return col_map[col]
        elif role == Qt.ItemDataRole.DecorationRole:
            if col == 1:
                cache_id = f"{self.browser}!{profile_id}"
                if cache_id in self.profile_pic_cache:
                    return self.profile_pic_cache[cache_id]
                else:
                    pic = get_profile_picture(self.browser, profile)
                    self.profile_pic_cache[cache_id] = pic
                    return pic
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
        return None

    def update_data(self, browser: str, profiles: dict[str, Profile]):
        self.beginResetModel()

        self.browser = browser
        self.profiles = profiles
        self.profile_ids = list(profiles.keys())
        self.profile_ids.sort(key=sort_profiles_id_func)

        self.profile_pic_cache.clear()

        self.endResetModel()


class ProfilesTable(TreeView):

    def __init__(
            self,
            name: str,
            browser: str = "",
            profiles: dict[str, Profile] = None,
            userdata_dir: str = "",
            exec_path: str = "",
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))
        self.browser = browser
        self.profiles = profiles or {}
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path

        self.menu_ctx = RoundMenu(parent=self)
        self.act_open = Action(icon=Fi.LINK, text="打开", parent=self)
        self.act_show_data = Action(icon=Fi.DICTIONARY, text="查看原始数据", parent=self)
        self.menu_ctx.addAction(self.act_open)
        self.menu_ctx.addSeparator()
        self.menu_ctx.addAction(self.act_show_data)

        self.setIndentation(0)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setUniformRowHeights(True)
        self.setIconSize(QSize(32, 32))

        self.profiles_model = ProfilesModel(browser, self.profiles, self)

        proxy_model = ProfileSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.profiles_model)

        self.setModel(proxy_model)

        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.act_open.triggered.connect(self.on_act_open_triggered)
        self.act_show_data.triggered.connect(self.on_act_show_data_triggered)
        self.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.scrollDelagate = None

    def on_act_open_triggered(self):
        open_profiles(self, self.selectedIndexes(), self.exec_path, self.userdata_dir)

    def on_act_show_data_triggered(self):
        profile_ids = [index.data(Qt.ItemDataRole.DisplayRole)
                       for index in self.selectedIndexes()
                       if index.column() == 0]
        if len(profile_ids) == 0:
            show_quick_tip(self, "提示", "你没有选中任何用户。")
            return
        # 只取第一个用户的
        profile = self.profiles[profile_ids[0]]
        # dr = DaRawData(profile.raw_data, self)
        # dr.show()

    def on_custom_context_menu_requested(self, pos: QPoint):
        self.menu_ctx.exec(self.viewport().mapToGlobal(pos))

    def update_model(
            self,
            browser: str,
            profiles: dict[str, Profile],
            userdata_dir: str,
            exec_path: str,
    ):
        self.browser = browser
        self.profiles = profiles
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.profiles_model.update_data(browser, profiles)

        self.setColumnWidth(1, 250)
