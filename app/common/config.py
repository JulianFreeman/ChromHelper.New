from qfluentwidgets import (
    QConfig, qconfig, Theme, BoolValidator, ConfigItem,
    SmoothMode, OptionsValidator, EnumSerializer, OptionsConfigItem,
)


class Config(QConfig):

    switch_animation = ConfigItem("Personalize", "SwitchAnimation", False,
                                  BoolValidator(), restart=True)
    smooth_mode = OptionsConfigItem("Personalize", "SmoothMode", SmoothMode.NO_SMOOTH,
                                    OptionsValidator(SmoothMode), EnumSerializer(SmoothMode), restart=True)


cfg = Config()
cfg.themeMode.value = Theme.LIGHT
qconfig.load("config.json", cfg)
