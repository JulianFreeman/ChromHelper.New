import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtCore import Qt, QModelIndex, QAbstractListModel, Signal
from PySide6.QtGui import QIcon
from qfluentwidgets import (
    CardWidget, IconWidget, BodyLabel, CaptionLabel, TransparentToolButton,
    setFont, ScrollArea, PrimaryPushButton, PushButton, MessageBoxBase,
    ModelComboBox, LineEdit, TeachingTip, InfoBarIcon, TeachingTipTailPosition,
    FluentIconBase,
)
from qfluentwidgets import FluentIcon as Fi
from app.common.utils import get_icon_path, SUPPORTED_BROWSERS, accept_warning
from app.chromy import get_browser_exec_path, get_browser_data_path
from app.database.db_operations import DBManger


class TTButtonWithItem(TransparentToolButton):

    clicked_with_item = Signal(object)

    def __init__(self, item: object, icon: str | QIcon | FluentIconBase, parent: QWidget = None):
        super().__init__(parent)
        self.setIcon(icon)
        self.item = item
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_item.emit(self.item)


class IconListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon_names = SUPPORTED_BROWSERS.copy()

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.icon_names)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        if role == Qt.ItemDataRole.EditRole:
            return self.icon_names[row]
        if role == Qt.ItemDataRole.DecorationRole:
            return QIcon(get_icon_path(self.icon_names[row]))
        return None


class UserDataAddDialog(MessageBoxBase):

    def __init__(self, exists_names: list[str], parent: QWidget = None):
        super().__init__(parent)
        self.exists_names = exists_names

        self.cw = QWidget(self)
        self.vly_m = QVBoxLayout()
        self.cw.setLayout(self.vly_m)

        self.hly_icon = QHBoxLayout()
        self.hly_name = QHBoxLayout()
        self.hly_exec = QHBoxLayout()
        self.hly_data = QHBoxLayout()
        self.vly_m.addLayout(self.hly_icon)
        self.vly_m.addLayout(self.hly_name)
        self.vly_m.addLayout(self.hly_exec)
        self.vly_m.addLayout(self.hly_data)

        self.lb_icon = BodyLabel("图　　　　标", self.cw)
        self.cmbx_icons = ModelComboBox(self.cw)
        self.cmbx_icons.setMinimumWidth(150)
        self.icon_model = IconListModel(self.cw)
        self.cmbx_icons.setModel(self.icon_model)

        self.hly_icon.addWidget(self.lb_icon)
        self.hly_icon.addStretch(1)
        self.hly_icon.addWidget(self.cmbx_icons)

        self.lb_name = BodyLabel("名　　　　称", self.cw)
        self.lne_name = LineEdit(self.cw)
        self.lne_name.setMinimumWidth(150)
        self.hly_name.addWidget(self.lb_name)
        self.hly_name.addStretch(1)
        self.hly_name.addWidget(self.lne_name)

        self.lb_exec = BodyLabel("执行文件路径", self.cw)
        self.lne_exec = LineEdit(self.cw)
        self.pbn_exec = PushButton("选择", self.cw)
        self.pbn_exec.setMinimumWidth(80)
        self.hly_exec.addWidget(self.lb_exec)
        self.hly_exec.addWidget(self.lne_exec)
        self.hly_exec.addWidget(self.pbn_exec)
        self.hly_exec.setSpacing(8)

        self.lb_data = BodyLabel("用户数据路径", self.cw)
        self.lne_data = LineEdit(self.cw)
        self.pbn_data = PushButton("选择", self.cw)
        self.pbn_data.setMinimumWidth(80)
        self.hly_data.addWidget(self.lb_data)
        self.hly_data.addWidget(self.lne_data)
        self.hly_data.addWidget(self.pbn_data)
        self.hly_data.setSpacing(8)

        self.viewLayout.addWidget(self.cw)

        self.yesButton.setText("保存")
        self.buttonLayout.insertStretch(0, 3)

        self.widget.setMinimumWidth(800)

        self.cmbx_icons.currentIndexChanged.connect(self.on_cmbx_icons_current_index_changed)
        self.pbn_exec.clicked.connect(self.on_pbn_exec_clicked)
        self.pbn_data.clicked.connect(self.on_pbn_data_clicked)

        # 手动触发一次
        self.cmbx_icons.setCurrentIndex(0)

    def on_cmbx_icons_current_index_changed(self, index: int):
        browser = self.icon_model.icon_names[index]
        browser_path = get_browser_exec_path(browser)
        if browser_path is not None:
            self.lne_exec.setText(browser_path)
        else:
            self.lne_exec.clear()
        # 如果真的要添加，那肯定是除了默认位置之外的，所以这里就不填充了
        # 因为默认的位置可以在初始化时自动填充，如果默认的没了，就重置数据库吧

    def on_pbn_exec_clicked(self):
        browser = self.cmbx_icons.currentText()
        exec_path = get_browser_exec_path(browser)
        if exec_path is None:
            p = os.path.expanduser("~")
        else:
            p = str(Path(exec_path).parent)
        filename, _ = QFileDialog.getOpenFileName(self, "打开执行文件", p)  # type: (str, str)
        if len(filename) == 0:
            return

        # MacOS 的执行文件只通过 QFileDialog 选不到，所以手动加
        if sys.platform == "darwin":
            filename_p = Path(filename)
            if filename_p.is_dir() and filename.endswith(".app"):
                name = filename_p.stem
                filename = str(filename_p / "Contents" / "MacOS" / name)

        self.lne_exec.setText(filename)

    def on_pbn_data_clicked(self):
        browser = self.cmbx_icons.currentText()
        data_path = get_browser_data_path(browser)
        if data_path is None:
            d = os.path.expanduser("~")
        else:
            d = str(Path(data_path).parent)
        dirname = QFileDialog.getExistingDirectory(self, "打开用户数据目录", d)
        if len(dirname) == 0:
            return

        self.lne_data.setText(dirname)

    def validate(self):
        if len(self.lne_name.text()) == 0:
            TeachingTip.create(
                target=self.lne_name,
                title="错误",
                content="名称不能为空！",
                icon=InfoBarIcon.ERROR,
                isClosable=True,
                duration=2000,
                tailPosition=TeachingTipTailPosition.RIGHT,
                parent=self,
            )
            return False
        if len(self.lne_data.text()) == 0:
            TeachingTip.create(
                target=self.lne_data,
                title="错误",
                content="用户路径不能为空！",
                icon=InfoBarIcon.ERROR,
                isClosable=True,
                duration=2000,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                parent=self,
            )
            return False
        if accept_warning(self, len(self.lne_exec.text()) == 0, "警告",
                          "如果执行文件路径为空，不影响查看，但无法打开浏览器窗口，要继续吗？"):
            return False

        if self.lne_name.text() in self.exists_names:
            TeachingTip.create(
                target=self.lne_name,
                title="错误",
                content="该名称已存在，请更换一个。",
                icon=InfoBarIcon.ERROR,
                isClosable=True,
                duration=2000,
                tailPosition=TeachingTipTailPosition.RIGHT,
                parent=self,
            )
            return False

        return True


class UserDataCard(CardWidget):

    def __init__(
            self,
            name: str,
            type_: str,
            exec_path: str,
            data_path: str,
            parent=None):
        super().__init__(parent)
        self.name = name  # 添加的时候检测名称是否存在用

        self.icon_widget = IconWidget(get_icon_path(type_), self)
        self.title_label = BodyLabel(name, self)
        setFont(self.title_label, 18)
        self.exec_label = CaptionLabel(exec_path, self)
        self.exec_label.setTextColor("#606060", "#d2d2d2")
        self.data_label = CaptionLabel(data_path, self)
        self.data_label.setTextColor("#606060", "#d2d2d2")
        self.close_button = TTButtonWithItem(self, Fi.CLOSE, self)

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


class UserDataCardList(ScrollArea):

    card_removed = Signal(UserDataCard)

    def __init__(self, dbm: DBManger, parent=None):
        super().__init__(parent)
        self.dbm = dbm
        self.cards: list[UserDataCard] = []

        self.cw = QWidget(self)
        self.setWidget(self.cw)

        self.vly_wg = QVBoxLayout()
        self.cw.setLayout(self.vly_wg)

        self.vly_wg.setSpacing(6)
        self.vly_wg.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.enableTransparentBackground()
        self.setWidgetResizable(True)

    def add_card(self, name: str, type_: str, exec_path: str, data_path: str):
        card = UserDataCard(name, type_, exec_path, data_path, self)
        self.vly_wg.addWidget(card, alignment=Qt.AlignmentFlag.AlignTop)
        card.close_button.clicked_with_item.connect(self.remove_card)
        self.cards.append(card)

    def remove_card(self, card: UserDataCard):
        self.vly_wg.removeWidget(card)
        self.cards.remove(card)
        card.deleteLater()

        self.card_removed.emit(card)


class ConfigInterface(QWidget):

    userdata_changed = Signal(bool)  # bool 的作用是告诉是否包含移除

    def __init__(self, name: str, dbm: DBManger, parent=None):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))
        self.dbm = dbm
        # 这里无所谓，后面 reset 的时候会填充这个数据，所以此时为空就行
        self.userdata_info = []  # [[name, type, exec, data]]

        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.hly_top = QHBoxLayout()
        self.hly_top.setContentsMargins(11, 0, 11, 0)
        self.pbn_add = PrimaryPushButton(self)
        self.pbn_add.setText("添加")
        self.pbn_add.setIcon(Fi.ADD)

        self.pbn_reset = PushButton(self)
        self.pbn_reset.setText("重置")
        self.pbn_reset.setIcon(Fi.UPDATE)
        self.hly_top.addWidget(self.pbn_add)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_reset)

        self.vly_m.addLayout(self.hly_top)
        self.card_list = UserDataCardList(dbm, self)
        self.vly_m.addWidget(self.card_list)

        self.pbn_add.clicked.connect(self.on_pbn_add_clicked)
        self.pbn_reset.clicked.connect(self.on_pbn_reset_clicked)
        self.card_list.card_removed.connect(self.on_card_removed)

        # 这个要在最后，第一次填充也相当于重置
        self.reset_cards(is_init=True)

    def on_pbn_add_clicked(self):
        exists_names = [c.name for c in self.card_list.cards]
        mb = UserDataAddDialog(exists_names, self)
        if mb.exec():
            name = mb.lne_name.text()
            type_ = mb.cmbx_icons.currentText()
            exec_path = mb.lne_exec.text()
            data_path = mb.lne_data.text()
            self.card_list.add_card(name, type_, exec_path, data_path)
            self.dbm.insert_one(name, type_, exec_path, data_path)
            self.userdata_changed.emit(False)

    def on_pbn_reset_clicked(self):
        # 下面的函数会触发信号，所以这里就不触发了
        self.reset_cards()

    def on_card_removed(self, card: UserDataCard):
        self.dbm.delete_one(card.name)
        self.userdata_changed.emit(True)

    def reset_cards(self, is_init: bool = False):
        # 清空卡片
        while len(self.card_list.cards) > 0:
            card = self.card_list.cards[-1]
            # 这里可能每移除一次就会触发一次信号，但是因为总量不会大，就这样吧
            self.card_list.remove_card(card)

        # 如果是打开软件，就不重置，因为还会想保留上次的路径
        if not is_init:
            self.dbm.reset()
        # 填充数据
        self.userdata_info = self.dbm.select_all()
        # 填充卡片
        for name, type_, exec_path, data_path in self.userdata_info:
            self.card_list.add_card(name, type_, exec_path, data_path)

        self.userdata_changed.emit(True)
