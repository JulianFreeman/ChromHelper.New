# coding: utf8
from typing import Any
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import MessageBoxBase, TreeView, SmoothMode

from app.common.config import cfg


# 以下两个类生成自 ChatGPT，并做了修改
class DictTreeItem(object):
    def __init__(self, key: str = "", value: Any = None, parent: "DictTreeItem" = None):
        self.key = key
        self.value = value
        self.parent_item = parent
        self.child_items: list[DictTreeItem] = []

    def append_child(self, child: "DictTreeItem"):
        self.child_items.append(child)

    def child(self, row: int):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    @staticmethod
    def column_count():
        return 2  # 我们定义两列，一列为键，一列为值

    def parent(self):
        return self.parent_item


class RawDataModel(QAbstractItemModel):

    def __init__(self, raw_data: dict, parent: QObject = None):
        super().__init__(parent)
        self.root_item = DictTreeItem("Root")
        self.setup_model_data(raw_data, self.root_item)

    def setup_model_data(self, raw_data: dict, parent: DictTreeItem):
        if isinstance(raw_data, dict):
            for key, value in raw_data.items():
                item = DictTreeItem(key, "" if isinstance(value, dict) else value, parent)
                parent.append_child(item)
                if isinstance(value, dict):
                    self.setup_model_data(value, item)

    def rowCount(self, parent: QModelIndex = ...):
        if not parent.isValid():
            return self.root_item.child_count()
        parent_item = parent.internalPointer()
        return parent_item.child_count()

    def columnCount(self, parent: QModelIndex = ...):
        return 2  # 我们定义两列

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.key
            elif index.column() == 1:
                return item.value
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return "键"
            elif section == 1:
                return "值"
        return None

    def index(self, row: int, column: int, parent: QModelIndex = ...):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)


class RawDataDialog(MessageBoxBase):

    def __init__(self, data: dict, parent: QWidget = None):
        super().__init__(parent)
        self.setClosableOnMaskClicked(True)

        self.cw = QWidget(self)
        self.vly_m = QVBoxLayout()
        self.cw.setLayout(self.vly_m)

        self.trv_m = TreeView(self.cw)
        self.trv_m.scrollDelagate.verticalSmoothScroll.setSmoothMode(cfg.get(cfg.smooth_mode))
        self.vly_m.addWidget(self.trv_m)

        self.model = RawDataModel(data, parent=self)
        self.trv_m.setModel(self.model)

        self.viewLayout.addWidget(self.cw)
        self.trv_m.setColumnWidth(0, 300)

        self.widget.setMinimumSize(800, 640)

        self.buttonLayout.insertStretch(0, 4)
        self.cancelButton.hide()
