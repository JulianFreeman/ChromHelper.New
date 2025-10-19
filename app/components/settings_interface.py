from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from qfluentwidgets import (
    ScrollArea, ExpandLayout, SettingCardGroup,
    OptionsSettingCard, CustomColorSettingCard, setTheme, setThemeColor,
    SwitchSettingCard, InfoBar, InfoBarPosition
)
from qfluentwidgets import FluentIcon as Fi
from app.common.config import cfg


class SettingsInterface(ScrollArea):

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.setObjectName(name.replace(" ", "-"))
        self.cw = QWidget(self)
        self.ely = ExpandLayout(self.cw)
        self.setWidget(self.cw)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.enableTransparentBackground()

        self.personal_group = SettingCardGroup("个性化", self.cw)
        self.theme_card = OptionsSettingCard(
            cfg.themeMode,
            Fi.BRUSH,
            "应用主题",
            "修改应用的外观",
            texts=["浅色", "深色", "跟随系统"],
            parent=self.personal_group,
        )
        self.theme_color_card = CustomColorSettingCard(
            cfg.themeColor,
            Fi.PALETTE,
            "主题色",
            "修改应用的主题颜色",
            parent=self.personal_group,
        )
        self.switch_animation_card = SwitchSettingCard(
            Fi.SCROLL,
            "切换动画",
            "切换不同页面时是否显示动画",
            configItem=cfg.switch_animation,
            parent=self.personal_group,
        )
        self.smooth_mode_card = OptionsSettingCard(
            cfg.smooth_mode,
            Fi.LEAF,
            "滚动模式",
            "修改视图滚动模式",
            texts=["无滚动", "匀速滚动", "线性滚动", "二次缓动", "余弦平滑"],
            parent=self.personal_group,
        )

        self.personal_group.addSettingCard(self.theme_card)
        self.personal_group.addSettingCard(self.theme_color_card)
        self.personal_group.addSettingCard(self.switch_animation_card)
        self.personal_group.addSettingCard(self.smooth_mode_card)

        self.ely.setSpacing(28)
        self.ely.setContentsMargins(20, 20, 20, 20)
        self.ely.addWidget(self.personal_group)

        cfg.themeChanged.connect(setTheme)
        cfg.appRestartSig.connect(self.show_restart_tip)
        self.theme_color_card.colorChanged.connect(lambda c: setThemeColor(c))

    def show_restart_tip(self):
        InfoBar.warning("", "设置已更新，重启应用生效。", duration=5000,
                        position=InfoBarPosition.BOTTOM_RIGHT, parent=self.window())
