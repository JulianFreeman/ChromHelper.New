from pathlib import Path
from qfluentwidgets import (
    QConfig, qconfig, Theme, BoolValidator, ConfigItem,
    SmoothMode, OptionsValidator, EnumSerializer, OptionsConfigItem,
)
from app.common.utils import get_app_dir


class Config(QConfig):

    switch_animation = ConfigItem("Personalize", "SwitchAnimation", False,
                                  BoolValidator(), restart=True)
    smooth_mode = OptionsConfigItem("Personalize", "SmoothMode", SmoothMode.NO_SMOOTH,
                                    OptionsValidator(SmoothMode), EnumSerializer(SmoothMode), restart=True)


VERSION = '4.1.1'
ORG_NAME = "Oranje"
APP_NAME = "ChromHelper"
ZH_APP_NAME = "浏览器助手"
APP_DIR = get_app_dir(ORG_NAME, APP_NAME)
SENT_CACHE_FILE = Path(APP_DIR, "sent_ext.json")

cfg = Config()
cfg.themeMode.value = Theme.LIGHT
qconfig.load(str(Path(APP_DIR) / "config.json"), cfg)
