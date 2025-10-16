from typing import Callable

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPoint, QSize, QSortFilterProxyModel
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QTreeView
from qfluentwidgets import TreeView, RoundMenu, Action, SmoothMode
from qfluentwidgets import FluentIcon as Fi

from app.common.utils import accept_warning, get_icon_path, show_quick_tip
from app.common.utils import path_not_exist
from app.common.thread import run_some_task
from app.components.profiles_dialog import ShowProfilesDialog, ShowProfilesModel
from app.components.rawdata_dialog import RawDataDialog
from app.chromy.chromi import (
    Extension, Profile,
    sort_profiles_id_func,
    ProfileSortFilterProxyModel,
)
from app.common.config import cfg


class ExtensionsModel(QAbstractTableModel):

    def __init__(self, extensions: dict[str, Extension], parent=None):
        super().__init__(parent)
        self.extensions = extensions
        self.extension_ids = list(self.extensions.keys())
        self.headers = ["名称", "描述"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.extension_ids)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()
        ext = self.extensions[self.extension_ids[row]]
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return ext.name
            if col == 1:
                return ext.description
        elif role == Qt.ItemDataRole.DecorationRole:
            if col == 0:
                if path_not_exist(ext.icon):
                    return QIcon(get_icon_path("none"))
                else:
                    return QIcon(ext.icon)
        elif role == Qt.ItemDataRole.UserRole:
            # 任意一列都返回 id
            return ext.id
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
        return None

    def update_data(self, extensions: dict[str, Extension]):
        self.beginResetModel()
        self.extensions.clear()
        self.extensions.update(extensions)
        self.extension_ids = list(self.extensions.keys())

        self.endResetModel()


class ExtensionsTable(TreeView):

    def __init__(
            self,
            name: str,
            extensions: dict[str, Extension] = None,
            profiles: dict[str, Profile] = None,
            userdata_dir: str = "",
            exec_path: str = "",
            delete_func: Callable[[list[str], list[str]], None] = None,
            parent=None
    ):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))
        self.extensions = extensions or {}
        self.profiles = profiles or {}
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func

        self.menu_ctx = RoundMenu(parent=self)
        self.act_check = Action(icon=Fi.SEARCH, text="查看用户", parent=self)
        self.act_delete = Action(icon=Fi.DELETE, text="删除", parent=self)
        self.act_show_data = Action(icon=Fi.DICTIONARY, text="查看原始数据", parent=self)
        self.menu_ctx.addAction(self.act_check)
        self.menu_ctx.addAction(self.act_delete)
        self.menu_ctx.addSeparator()
        self.menu_ctx.addAction(self.act_show_data)

        self.setIndentation(0)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setUniformRowHeights(True)
        self.setStyleSheet("QTreeView::item { height: 40px; }")
        self.setIconSize(QSize(32, 32))

        self.extensions_model = ExtensionsModel(self.extensions, self)
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.extensions_model)
        self.setModel(proxy_model)

        self.doubleClicked.connect(self.on_double_clicked)
        self.act_check.triggered.connect(self.on_act_check_triggered)
        self.act_delete.triggered.connect(self.on_act_delete_triggered)
        self.act_show_data.triggered.connect(self.on_act_show_data_triggered)
        self.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(cfg.get(cfg.smooth_mode))

    def on_act_delete_triggered(self):
        ext_ids = [index.data(Qt.ItemDataRole.UserRole)
                   for index in self.selectedIndexes()
                   if index.column() == 0]
        if len(ext_ids) == 0:
            show_quick_tip(self, "警告", "你没有选中任何插件。")
            return

        profile_ids = set()
        for ext_id in ext_ids:
            profile_ids = profile_ids.union(self.extensions[ext_id].profiles)

        if accept_warning(self, True, "警告",
                          f"你确定要删除这 {len(ext_ids)} 个插件吗？"):
            return

        run_some_task("正在删除，请稍等……", self,
                      self.delete_func, ext_ids, profile_ids)
        self.update_after_deletion()

    def on_act_show_data_triggered(self):
        extension_ids = [index.data(Qt.ItemDataRole.UserRole)
                         for index in self.selectedIndexes()
                         if index.column() == 0]
        if len(extension_ids) == 0:
            show_quick_tip(self, "提示", "你没有选中任何插件。")
            return
        # 只取第一个用户的
        extension = self.extensions[extension_ids[0]]
        dr = RawDataDialog(extension.raw_data, self)
        dr.show()

    def on_act_check_triggered(self):
        if len(self.selectedIndexes()) == 0:
            show_quick_tip(self, "提示", "你没有选中任何插件。")
            return
        index = self.selectedIndexes()[0]
        self.on_double_clicked(index)

    def on_custom_context_menu_requested(self, pos: QPoint):
        self.menu_ctx.exec(self.viewport().mapToGlobal(pos))

    def on_double_clicked(self, index: QModelIndex):
        ext_id: str = index.data(Qt.ItemDataRole.UserRole)
        ext = self.extensions[ext_id]

        show_profile_ids = list(ext.profiles)
        show_profile_ids.sort(key=sort_profiles_id_func)
        show_profiles: list[list[str]] = []
        for profile_id in show_profile_ids:
            profile = self.profiles[profile_id]
            show_profiles.append([profile.id, profile.name, ""])

        model = ShowProfilesModel(show_profiles, self)
        proxy_model = ProfileSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)

        ds = ShowProfilesDialog(
            ext.name, ext.icon, ext.id,
            self.userdata_dir, self.exec_path, self.delete_func, self
        )
        ds.trv_p.setModel(proxy_model)

        ds.deletion_finished.connect(self.update_after_deletion)
        ds.exec()

    def update_after_deletion(self):
        self.extensions_model.update_data(self.extensions)

    def update_model(
            self,
            extensions: dict[str, Extension],
            profiles: dict[str, Profile],
            userdata_dir: str,
            exec_path: str,
            delete_func: Callable[[list[str], list[str]], None]
    ):
        self.profiles = profiles
        self.extensions = extensions
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func
        self.extensions_model.update_data(extensions)

        self.setColumnWidth(0, 250)
