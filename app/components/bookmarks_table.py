from typing import Callable

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPoint, QSortFilterProxyModel
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTreeView, QWidget
from qfluentwidgets import TreeView, RoundMenu, Action, SmoothMode
from qfluentwidgets import FluentIcon as Fi

from app.common.utils import  accept_warning, show_quick_tip, get_icon_path
from app.chromy.chromi import Bookmark, Profile, sort_profiles_id_func, ProfileSortFilterProxyModel
from app.components.profiles_dialog import ShowProfilesDialog, ShowProfilesModel
from app.common.thread import run_some_task


class BookmarksModel(QAbstractTableModel):

    def __init__(self, bookmarks: dict[str, Bookmark], parent=None):
        super().__init__(parent)
        self.bookmarks = bookmarks
        self.bookmark_urls = list(self.bookmarks.keys())

        self.headers = ["名称", "URL"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.bookmark_urls)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()
        bmk = self.bookmarks[self.bookmark_urls[row]]
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return bmk.name
            if col == 1:
                return bmk.url
        elif role == Qt.ItemDataRole.UserRole:
            return bmk.url
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font
        return None

    def update_data(self, bookmarks: dict[str, Bookmark]):
        self.beginResetModel()
        # 避免报错
        self.bookmarks.clear()
        self.bookmarks.update(bookmarks)
        self.bookmark_urls = list(self.bookmarks.keys())

        self.endResetModel()


class BookmarksTable(TreeView):

    def __init__(
            self,
            name: str,
            bookmarks: dict[str, Bookmark] = None,
            profiles: dict[str, Profile] = None,
            userdata_dir: str = "",
            exec_path: str = "",
            delete_func: Callable[[list[str], list[str]], None] = None,
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))
        self.bookmarks = bookmarks or {}
        self.profiles = profiles or {}
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func

        self.menu_ctx = RoundMenu(parent=self)
        self.act_check = Action(icon=Fi.SEARCH, text="查看用户", parent=self)
        self.act_delete = Action(icon=Fi.DELETE, text="删除", parent=self)
        self.menu_ctx.addAction(self.act_check)
        self.menu_ctx.addAction(self.act_delete)

        self.setIndentation(0)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.bookmarks_model = BookmarksModel(self.bookmarks, self)
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.bookmarks_model)

        self.setModel(proxy_model)

        self.doubleClicked.connect(self.on_double_clicked)
        self.act_check.triggered.connect(self.on_act_check_triggered)
        self.act_delete.triggered.connect(self.on_act_delete_triggered)
        self.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

    def on_act_delete_triggered(self):
        urls = [index.data(Qt.ItemDataRole.UserRole)
                for index in self.selectedIndexes()
                if index.column() == 0]
        if len(urls) == 0:
            show_quick_tip(self, "警告", "你没有选中任何书签。")
            return

        profile_ids = set()
        for url in urls:
            profile_ids = profile_ids.union(self.bookmarks[url].profiles.keys())

        if accept_warning(self, True, "警告",
                          f"你确定要删除这 {len(urls)} 个书签吗？"):
            return

        run_some_task("正在删除，请稍等……", self,
                      self.delete_func, urls, profile_ids)
        self.update_after_deletion()

    def on_act_check_triggered(self):
        if len(self.selectedIndexes()) == 0:
            show_quick_tip(self, "提示", "你没有选中任何书签。")
            return
        index = self.selectedIndexes()[0]
        self.on_double_clicked(index)

    def on_custom_context_menu_requested(self, pos: QPoint):
        self.menu_ctx.exec(self.viewport().mapToGlobal(pos))

    def on_double_clicked(self, index: QModelIndex):
        url: str = index.data(Qt.ItemDataRole.UserRole)
        bmk = self.bookmarks[url]

        show_profile_ids = list(bmk.profiles.keys())
        show_profile_ids.sort(key=sort_profiles_id_func)
        show_profiles: list[list[str]] = []
        for profile_id in show_profile_ids:
            profile = self.profiles[profile_id]
            show_profiles.append([profile.id, profile.name, bmk.profiles[profile_id]])

        model = ShowProfilesModel(show_profiles, self)
        proxy_model = ProfileSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)

        ds = ShowProfilesDialog(
            bmk.name, get_icon_path("bookmark"), bmk.url,
            self.userdata_dir, self.exec_path, self.delete_func, self
        )
        ds.trv_p.setModel(proxy_model)

        ds.deletion_finished.connect(self.update_after_deletion)
        ds.exec()

    def update_after_deletion(self):
        self.bookmarks_model.update_data(self.bookmarks)

    def update_model(
            self,
            bookmarks: dict[str, Bookmark],
            profiles: dict[str, Profile],
            userdata_dir: str,
            exec_path: str,
            delete_func: Callable[[list[str], list[str]], None],
    ):
        self.bookmarks = bookmarks
        self.profiles = profiles
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func
        self.bookmarks_model.update_data(bookmarks)

        self.setColumnWidth(0, 300)
