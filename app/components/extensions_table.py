from typing import Callable

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPoint, QSize, QSortFilterProxyModel
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QTreeView, QStyleOptionViewItem, QApplication, QStyle
)
from qfluentwidgets import TreeView, RoundMenu, Action, TreeItemDelegate
from qfluentwidgets import FluentIcon as Fi

from app.common.utils import accept_warning, get_icon_path, show_quick_tip
from app.common.utils import path_not_exist, SafeMark, SAFE_MAP, SAFE_MAP_ICON
from app.common.thread import run_some_task
from app.components.profiles_dialog import ShowProfilesDialog, ShowProfilesModel
from app.components.rawdata_dialog import RawDataDialog
from app.chromy.chromi import (
    Extension, Profile,
    sort_profiles_id_func,
    ProfileSortFilterProxyModel,
)
from app.common.config import cfg

# ColumnIconDelegate 来自 Gemini，我看不懂。

class ColumnIconDelegate(TreeItemDelegate):
    """
    一个自定义委托，用于根据列号绘制不同大小的图标
    """

    def __init__(self, small_size: QSize, large_size: QSize, parent=None):
        super().__init__(parent)
        self.small_size = small_size
        self.large_size = large_size

    def paint(self, painter, option, index: QModelIndex):
        """
        重写 paint 方法
        """
        # 1. 复制一份 style option，以免修改原始 option
        #    注意：在 Python 中，option 是可变对象，
        #    但 QStyleOptionViewItem 推荐的方式是创建一个副本来修改
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)  # 用索引信息初始化副本

        # 2. 根据列号修改图标大小 (decorationSize)
        if index.column() == 0:
            # 第 0 列：大图标
            opt.decorationSize = self.large_size
        elif index.column() == 1:
            # 第 1 列：小图标
            opt.decorationSize = self.small_size
        else:
            # 其他列：使用视图的默认图标大小
            if opt.widget:
                opt.decorationSize = opt.widget.iconSize()

        # 3. 使用修改后的 option 调用父类的 paint 方法
        # 我们不直接调用 super().paint()，而是通过 style 来绘制
        # 这样可以确保所有样式（如选中、悬停）都正确
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """
        重写 sizeHint 方法
        """
        # 1. 复制一份 option
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        # 2. 根据列号修改图标大小 (decorationSize)
        if index.column() == 0:
            opt.decorationSize = self.large_size
        elif index.column() == 1:
            opt.decorationSize = self.small_size
        else:
            if opt.widget:
                opt.decorationSize = opt.widget.iconSize()

        # 3. 使用修改后的 option 调用父类的 sizeHint
        # 同样，我们通过 style 来获取正确的尺寸
        style = opt.widget.style() if opt.widget else QApplication.style()
        size = style.sizeFromContents(QStyle.ContentsType.CT_ItemViewItem, opt, QSize(), opt.widget)

        # 确保高度至少和图标一样高
        if index.column() == 0:
            size.setHeight(max(size.height(), self.large_size.height()))
        elif index.column() == 1:
            size.setHeight(max(size.height(), self.small_size.height()))

        return size


class ExtensionsModel(QAbstractTableModel):

    def __init__(self, extensions: dict[str, Extension],
                 ext_safe_marks: dict[str, SafeMark], parent=None):
        super().__init__(parent)
        self.extensions = extensions
        self.ext_safe_marks = ext_safe_marks
        self.extension_ids = list(self.extensions.keys())
        self.headers = ["名称", "安全性", "描述"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.extension_ids)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()
        ext_id = self.extension_ids[row]
        ext = self.extensions[ext_id]
        safe = self.ext_safe_marks[ext_id].safe if ext_id in self.ext_safe_marks else -2
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return ext.name
            if col == 1:
                return SAFE_MAP[safe]
            if col == 2:
                return ext.description
        elif role == Qt.ItemDataRole.DecorationRole:
            if col == 0:
                if path_not_exist(ext.icon):
                    return QIcon(get_icon_path("none"))
                else:
                    return QIcon(ext.icon)
            if col == 1:
                return SAFE_MAP_ICON[safe]
        elif role == Qt.ItemDataRole.UserRole:
            # 任意一列都返回 id 和安全标记
            return ext.id, safe
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
        return None

    def update_data(self, extensions: dict[str, Extension], ext_safe_marks: dict[str, SafeMark]):
        self.beginResetModel()
        self.extensions.clear()
        self.extensions.update(extensions)
        self.extension_ids = list(self.extensions.keys())

        self.ext_safe_marks.clear()
        self.ext_safe_marks.update(ext_safe_marks)

        self.endResetModel()

    def update_safe_marks(self, ext_safe_marks: dict[str, SafeMark]):
        self.beginResetModel()
        self.ext_safe_marks.clear()
        self.ext_safe_marks.update(ext_safe_marks)
        self.endResetModel()


class SafeFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.accepted_status = set()

    def set_accepted_status(self, status: list[int]):
        self.accepted_status = set(status)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent, /):
        index = self.sourceModel().index(source_row, 1, source_parent)
        safe: int = self.sourceModel().data(index, Qt.ItemDataRole.UserRole)[1]
        return safe in self.accepted_status


class ExtensionsTable(TreeView):

    def __init__(
            self,
            name: str,
            extensions: dict[str, Extension] = None,
            profiles: dict[str, Profile] = None,
            userdata_dir: str = "",
            exec_path: str = "",
            delete_func: Callable[[list[str], list[str]], None] = None,
            ext_safe_marks: dict[str, SafeMark] = None,
            parent=None
    ):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))
        self.extensions = extensions or {}
        self.profiles = profiles or {}
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func
        self.ext_safe_marks = ext_safe_marks or {}

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

        s_size = QSize(16, 16)
        l_size = QSize(32, 32)
        # 这个使插件表格丢失了高亮显示，不过也无所谓吧
        delegate = ColumnIconDelegate(s_size, l_size, self)
        self.setItemDelegate(delegate)

        self.extensions_model = ExtensionsModel(self.extensions, self.ext_safe_marks, self)
        self.filter_model = SafeFilterProxyModel(self)
        self.filter_model.setSourceModel(self.extensions_model)
        self.setModel(self.filter_model)

        self.doubleClicked.connect(self.on_double_clicked)
        self.act_check.triggered.connect(self.on_act_check_triggered)
        self.act_delete.triggered.connect(self.on_act_delete_triggered)
        self.act_show_data.triggered.connect(self.on_act_show_data_triggered)
        self.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(cfg.get(cfg.smooth_mode))

    def on_act_delete_triggered(self):
        ext_ids = [index.data(Qt.ItemDataRole.UserRole)[0]
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
        extension_ids = [index.data(Qt.ItemDataRole.UserRole)[0]
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
        ext_id: str = index.data(Qt.ItemDataRole.UserRole)[0]
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
        self.extensions_model.update_data(self.extensions, self.ext_safe_marks)

    def update_model(
            self,
            extensions: dict[str, Extension],
            profiles: dict[str, Profile],
            userdata_dir: str,
            exec_path: str,
            delete_func: Callable[[list[str], list[str]], None],
            ext_safe_marks: dict[str, SafeMark],
    ):
        self.profiles = profiles
        self.extensions = extensions
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func
        self.ext_safe_marks = ext_safe_marks
        self.extensions_model.update_data(extensions, ext_safe_marks)

        self.setColumnWidth(0, 250)

    def update_safe_marks(self, ext_safe_marks: dict[str, SafeMark]):
        self.ext_safe_marks = ext_safe_marks
        self.extensions_model.update_safe_marks(ext_safe_marks)
