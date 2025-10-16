# coding: utf8
from typing import Callable

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QVBoxLayout, QWidget,
)
from qfluentwidgets import (
    MessageBoxBase, TreeView, PushButton, PrimaryPushButton,
    BodyLabel, CaptionLabel, ImageLabel
)

from app.common.utils import accept_warning, show_quick_tip
from app.chromy.chromi import open_profiles
from app.common.thread import run_some_task


class ShowProfilesModel(QAbstractTableModel):

    def __init__(self, show_profiles: list[list[str]], parent=None):
        super().__init__(parent)
        self.show_profiles = show_profiles

        self.headers = ["ID", "名称", "位置"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.show_profiles)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.show_profiles[index.row()][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
        return None


class ProfileCard(QWidget):
    """ Profile card """

    def __init__(self, icon: str, name: str, id_: str, parent=None):
        super().__init__(parent=parent)
        self.icon_widget = ImageLabel(icon, self)
        self.name_label = BodyLabel(name, self)
        self.id_label = CaptionLabel(id_, self)
        self.id_label.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

        self.setFixedHeight(72)
        self.icon_widget.setScaledSize(QSize(48, 48))
        self.icon_widget.move(2, 6)
        self.name_label.move(64, 10)
        self.id_label.move(64, 30)


class ShowProfilesDialog(MessageBoxBase):

    deletion_finished = Signal()

    def __init__(
            self,
            name: str,
            icon: str,
            id_: str,
            userdata_dir: str,
            exec_path: str,
            delete_func: Callable[[list[str], list[str]], None],
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.id_ = id_
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func
        self.setClosableOnMaskClicked(True)

        self.cw = QWidget(self)
        self.vly_m = QVBoxLayout()
        self.cw.setLayout(self.vly_m)

        self.p = ProfileCard(icon, name, id_, self)
        self.vly_m.addWidget(self.p)

        self.trv_p = TreeView(self.cw)
        self.trv_p.setIndentation(0)
        self.trv_p.setSortingEnabled(True)
        self.trv_p.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.trv_p.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.vly_m.addWidget(self.trv_p)

        self.pbn_delete = PushButton("删除所选", self.cw)
        self.pbn_open = PrimaryPushButton("打开", self.cw)

        self.yesButton.hide()
        self.cancelButton.setText("取消")
        self.buttonLayout.insertWidget(0, self.pbn_delete, alignment=Qt.AlignmentFlag.AlignLeft)
        self.buttonLayout.insertStretch(1, 1)
        self.buttonLayout.insertWidget(2, self.pbn_open, alignment=Qt.AlignmentFlag.AlignLeft)
        self.buttonLayout.setStretch(4, 0)

        self.pbn_delete.setMinimumWidth(80)
        self.pbn_open.setMinimumWidth(80)
        self.cancelButton.setMinimumWidth(80)

        self.viewLayout.addWidget(self.cw)
        self.widget.setMinimumSize(600, 540)

        self.pbn_open.clicked.connect(self.on_pbn_open_clicked)
        self.pbn_delete.clicked.connect(self.on_pbn_delete_clicked)

    def on_pbn_open_clicked(self):
        open_profiles(self, self.trv_p.selectedIndexes(), self.exec_path, self.userdata_dir)

    def on_pbn_delete_clicked(self):
        profile_ids_to_delete = [index.data(Qt.ItemDataRole.DisplayRole)
                                 for index in self.trv_p.selectedIndexes()
                                 if index.column() == 0]
        if len(profile_ids_to_delete) == 0:
            show_quick_tip(self, "警告", "你没有选中任何用户。")
            return
        if accept_warning(self, True, "警告",
                          f"你确定删除这 {len(profile_ids_to_delete)} 个吗？"):
            return

        run_some_task("正在删除，请稍等……", self,
                      self.delete_func, [self.id_], profile_ids_to_delete)
        self.deletion_finished.emit()
        self.accept()
