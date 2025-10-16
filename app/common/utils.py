from pathlib import Path
from PySide6.QtWidgets import QWidget
from qfluentwidgets import MessageBox

SUPPORTED_BROWSERS = ["chrome", "edge", "brave", "vivaldi", "yandex", "chromium"]

icons_map = {
    "chrome": ":/images/icons/chrome_32.png",
    "edge": ":/images/icons/edge_32.png",
    "brave": ":/images/icons/brave_32.png",
    "vivaldi": ":/images/icons/vivaldi_32.png",
    "yandex": ":/images/icons/yandex_32.png",
    "chromium": ":/images/icons/chromium_32.png",
    "profile": ":/images/icons/profile_32.png",
    "extension": ":/images/icons/extension_32.png",
    "bookmark": ":/images/icons/bookmark_32.png",
    "config": ":/images/icons/config_32.png",
    "none": ":/images/icons/none_128.png",
    "settings": ":/images/icons/settings_32.png",
    "debug": ":/images/icons/debug_32.png",

    "chrome_avatars": {
        "IDR_PROFILE_AVATAR_27": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_27.png",
        "IDR_PROFILE_AVATAR_28": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_28.png",
        "IDR_PROFILE_AVATAR_29": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_29.png",
        "IDR_PROFILE_AVATAR_30": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_30.png",
        "IDR_PROFILE_AVATAR_31": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_31.png",
        "IDR_PROFILE_AVATAR_32": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_32.png",
        "IDR_PROFILE_AVATAR_33": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_33.png",
        "IDR_PROFILE_AVATAR_34": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_34.png",
        "IDR_PROFILE_AVATAR_35": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_35.png",
        "IDR_PROFILE_AVATAR_36": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_36.png",
        "IDR_PROFILE_AVATAR_37": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_37.png",
        "IDR_PROFILE_AVATAR_38": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_38.png",
        "IDR_PROFILE_AVATAR_39": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_39.png",
        "IDR_PROFILE_AVATAR_40": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_40.png",
        "IDR_PROFILE_AVATAR_41": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_41.png",
        "IDR_PROFILE_AVATAR_42": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_42.png",
        "IDR_PROFILE_AVATAR_43": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_43.png",
        "IDR_PROFILE_AVATAR_44": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_44.png",
        "IDR_PROFILE_AVATAR_45": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_45.png",
        "IDR_PROFILE_AVATAR_46": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_46.png",
        "IDR_PROFILE_AVATAR_47": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_47.png",
        "IDR_PROFILE_AVATAR_48": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_48.png",
        "IDR_PROFILE_AVATAR_49": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_49.png",
        "IDR_PROFILE_AVATAR_50": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_50.png",
        "IDR_PROFILE_AVATAR_51": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_51.png",
        "IDR_PROFILE_AVATAR_52": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_52.png",
        "IDR_PROFILE_AVATAR_53": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_53.png",
        "IDR_PROFILE_AVATAR_54": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_54.png",
        "IDR_PROFILE_AVATAR_55": ":/images/avatars/chrome/IDR_PROFILE_AVATAR_55.png",
    },
    "brave_avatars": {
        "IDR_PROFILE_AVATAR_26": ":/images/avatars/brave/IDR_PROFILE_AVATAR_26.png",
        "IDR_PROFILE_AVATAR_56": ":/images/avatars/brave/IDR_PROFILE_AVATAR_56.png",
        "IDR_PROFILE_AVATAR_57": ":/images/avatars/brave/IDR_PROFILE_AVATAR_57.png",
        "IDR_PROFILE_AVATAR_58": ":/images/avatars/brave/IDR_PROFILE_AVATAR_58.png",
        "IDR_PROFILE_AVATAR_59": ":/images/avatars/brave/IDR_PROFILE_AVATAR_59.png",
        "IDR_PROFILE_AVATAR_60": ":/images/avatars/brave/IDR_PROFILE_AVATAR_60.png",
        "IDR_PROFILE_AVATAR_61": ":/images/avatars/brave/IDR_PROFILE_AVATAR_61.png",
        "IDR_PROFILE_AVATAR_62": ":/images/avatars/brave/IDR_PROFILE_AVATAR_62.png",
        "IDR_PROFILE_AVATAR_63": ":/images/avatars/brave/IDR_PROFILE_AVATAR_63.png",
        "IDR_PROFILE_AVATAR_64": ":/images/avatars/brave/IDR_PROFILE_AVATAR_64.png",
        "IDR_PROFILE_AVATAR_65": ":/images/avatars/brave/IDR_PROFILE_AVATAR_65.png",
        "IDR_PROFILE_AVATAR_66": ":/images/avatars/brave/IDR_PROFILE_AVATAR_66.png",
        "IDR_PROFILE_AVATAR_67": ":/images/avatars/brave/IDR_PROFILE_AVATAR_67.png",
        "IDR_PROFILE_AVATAR_68": ":/images/avatars/brave/IDR_PROFILE_AVATAR_68.png",
        "IDR_PROFILE_AVATAR_69": ":/images/avatars/brave/IDR_PROFILE_AVATAR_69.png",
        "IDR_PROFILE_AVATAR_70": ":/images/avatars/brave/IDR_PROFILE_AVATAR_70.png",
        "IDR_PROFILE_AVATAR_71": ":/images/avatars/brave/IDR_PROFILE_AVATAR_71.png",
        "IDR_PROFILE_AVATAR_72": ":/images/avatars/brave/IDR_PROFILE_AVATAR_72.png",
        "IDR_PROFILE_AVATAR_73": ":/images/avatars/brave/IDR_PROFILE_AVATAR_73.png",
        "IDR_PROFILE_AVATAR_74": ":/images/avatars/brave/IDR_PROFILE_AVATAR_74.png",
        "IDR_PROFILE_AVATAR_75": ":/images/avatars/brave/IDR_PROFILE_AVATAR_75.png",
        "IDR_PROFILE_AVATAR_76": ":/images/avatars/brave/IDR_PROFILE_AVATAR_76.png",
        "IDR_PROFILE_AVATAR_77": ":/images/avatars/brave/IDR_PROFILE_AVATAR_77.png",
        "IDR_PROFILE_AVATAR_78": ":/images/avatars/brave/IDR_PROFILE_AVATAR_78.png",
        "IDR_PROFILE_AVATAR_79": ":/images/avatars/brave/IDR_PROFILE_AVATAR_79.png",
        "IDR_PROFILE_AVATAR_80": ":/images/avatars/brave/IDR_PROFILE_AVATAR_80.png",
        "IDR_PROFILE_AVATAR_81": ":/images/avatars/brave/IDR_PROFILE_AVATAR_81.png",
        "IDR_PROFILE_AVATAR_82": ":/images/avatars/brave/IDR_PROFILE_AVATAR_82.png",
        "IDR_PROFILE_AVATAR_83": ":/images/avatars/brave/IDR_PROFILE_AVATAR_83.png",
        "IDR_PROFILE_AVATAR_84": ":/images/avatars/brave/IDR_PROFILE_AVATAR_84.png",
        "IDR_PROFILE_AVATAR_85": ":/images/avatars/brave/IDR_PROFILE_AVATAR_85.png",
        "IDR_PROFILE_AVATAR_86": ":/images/avatars/brave/IDR_PROFILE_AVATAR_86.png",
        "IDR_PROFILE_AVATAR_87": ":/images/avatars/brave/IDR_PROFILE_AVATAR_87.png",
        "IDR_PROFILE_AVATAR_88": ":/images/avatars/brave/IDR_PROFILE_AVATAR_88.png",
        "IDR_PROFILE_AVATAR_89": ":/images/avatars/brave/IDR_PROFILE_AVATAR_89.png",
    },
    "vivaldi_avatars": {
        "IDR_PROFILE_VIVALDI_AVATAR_0": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_0.png",
        "IDR_PROFILE_VIVALDI_AVATAR_1": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_1.png",
        "IDR_PROFILE_VIVALDI_AVATAR_2": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_2.png",
        "IDR_PROFILE_VIVALDI_AVATAR_3": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_3.png",
        "IDR_PROFILE_VIVALDI_AVATAR_4": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_4.png",
        "IDR_PROFILE_VIVALDI_AVATAR_5": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_5.png",
        "IDR_PROFILE_VIVALDI_AVATAR_6": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_6.png",
        "IDR_PROFILE_VIVALDI_AVATAR_7": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_7.png",
        "IDR_PROFILE_VIVALDI_AVATAR_8": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_8.png",
        "IDR_PROFILE_VIVALDI_AVATAR_9": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_9.png",
        "IDR_PROFILE_VIVALDI_AVATAR_10": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_10.png",
        "IDR_PROFILE_VIVALDI_AVATAR_11": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_11.png",
        "IDR_PROFILE_VIVALDI_AVATAR_12": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_12.png",
        "IDR_PROFILE_VIVALDI_AVATAR_13": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_13.png",
        "IDR_PROFILE_VIVALDI_AVATAR_14": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_14.png",
        "IDR_PROFILE_VIVALDI_AVATAR_15": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_15.png",
        "IDR_PROFILE_VIVALDI_AVATAR_16": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_16.png",
        "IDR_PROFILE_VIVALDI_AVATAR_17": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_17.png",
        "IDR_PROFILE_VIVALDI_AVATAR_18": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_18.png",
        "IDR_PROFILE_VIVALDI_AVATAR_19": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_19.png",
        "IDR_PROFILE_VIVALDI_AVATAR_20": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_20.png",
        "IDR_PROFILE_VIVALDI_AVATAR_21": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_21.png",
        "IDR_PROFILE_VIVALDI_AVATAR_22": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_22.png",
        "IDR_PROFILE_VIVALDI_AVATAR_23": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_23.png",
        "IDR_PROFILE_VIVALDI_AVATAR_24": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_24.png",
        "IDR_PROFILE_VIVALDI_AVATAR_25": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_25.png",
        "IDR_PROFILE_VIVALDI_AVATAR_26": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_26.png",
        "IDR_PROFILE_VIVALDI_AVATAR_27": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_27.png",
        "IDR_PROFILE_VIVALDI_AVATAR_28": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_28.png",
        "IDR_PROFILE_VIVALDI_AVATAR_29": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_29.png",
        "IDR_PROFILE_VIVALDI_AVATAR_30": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_30.png",
        "IDR_PROFILE_VIVALDI_AVATAR_31": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_31.png",
        "IDR_PROFILE_VIVALDI_AVATAR_32": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_32.png",
        "IDR_PROFILE_VIVALDI_AVATAR_33": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_33.png",
        "IDR_PROFILE_VIVALDI_AVATAR_34": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_34.png",
        "IDR_PROFILE_VIVALDI_AVATAR_35": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_35.png",
        "IDR_PROFILE_VIVALDI_AVATAR_36": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_36.png",
        "IDR_PROFILE_VIVALDI_AVATAR_37": ":/images/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_37.png",
    },
    "edge_avatars": {
        "IDR_PROFILE_AVATAR_20": ":/images/avatars/edge/IDR_PROFILE_AVATAR_20.png",
        "IDR_PROFILE_AVATAR_21": ":/images/avatars/edge/IDR_PROFILE_AVATAR_21.png",
        "IDR_PROFILE_AVATAR_22": ":/images/avatars/edge/IDR_PROFILE_AVATAR_22.png",
        "IDR_PROFILE_AVATAR_23": ":/images/avatars/edge/IDR_PROFILE_AVATAR_23.png",
        "IDR_PROFILE_AVATAR_24": ":/images/avatars/edge/IDR_PROFILE_AVATAR_24.png",
        "IDR_PROFILE_AVATAR_25": ":/images/avatars/edge/IDR_PROFILE_AVATAR_25.png",
        "IDR_PROFILE_AVATAR_26": ":/images/avatars/edge/IDR_PROFILE_AVATAR_26.png",
        "IDR_PROFILE_AVATAR_27": ":/images/avatars/edge/IDR_PROFILE_AVATAR_27.png",
        "IDR_PROFILE_AVATAR_28": ":/images/avatars/edge/IDR_PROFILE_AVATAR_28.png",
        "IDR_PROFILE_AVATAR_29": ":/images/avatars/edge/IDR_PROFILE_AVATAR_29.png",
        "IDR_PROFILE_AVATAR_30": ":/images/avatars/edge/IDR_PROFILE_AVATAR_30.png",
        "IDR_PROFILE_AVATAR_31": ":/images/avatars/edge/IDR_PROFILE_AVATAR_31.png",
        "IDR_PROFILE_AVATAR_32": ":/images/avatars/edge/IDR_PROFILE_AVATAR_32.png",
        "IDR_PROFILE_AVATAR_33": ":/images/avatars/edge/IDR_PROFILE_AVATAR_33.png",
        "IDR_PROFILE_AVATAR_34": ":/images/avatars/edge/IDR_PROFILE_AVATAR_34.png",
        "IDR_PROFILE_AVATAR_35": ":/images/avatars/edge/IDR_PROFILE_AVATAR_35.png",
        "IDR_PROFILE_AVATAR_36": ":/images/avatars/edge/IDR_PROFILE_AVATAR_36.png",
        "IDR_PROFILE_AVATAR_37": ":/images/avatars/edge/IDR_PROFILE_AVATAR_37.png",
        "IDR_PROFILE_AVATAR_38": ":/images/avatars/edge/IDR_PROFILE_AVATAR_38.png",
        "IDR_PROFILE_AVATAR_39": ":/images/avatars/edge/IDR_PROFILE_AVATAR_39.png",
        "IDR_PROFILE_AVATAR_40": ":/images/avatars/edge/IDR_PROFILE_AVATAR_40.png",
    },
    "yandex_avatars": {
        "IDR_PROFILE_AVATAR_YANDEX_0": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_0.png",
        "IDR_PROFILE_AVATAR_YANDEX_1": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_1.png",
        "IDR_PROFILE_AVATAR_YANDEX_2": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_2.png",
        "IDR_PROFILE_AVATAR_YANDEX_3": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_3.png",
        "IDR_PROFILE_AVATAR_YANDEX_4": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_4.png",
        "IDR_PROFILE_AVATAR_YANDEX_5": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_5.png",
        "IDR_PROFILE_AVATAR_YANDEX_6": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_6.png",
        "IDR_PROFILE_AVATAR_YANDEX_7": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_7.png",
        "IDR_PROFILE_AVATAR_YANDEX_8": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_8.png",
        "IDR_PROFILE_AVATAR_YANDEX_9": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_9.png",
        "IDR_PROFILE_AVATAR_YANDEX_10": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_10.png",
        "IDR_PROFILE_AVATAR_YANDEX_11": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_11.png",
        "IDR_PROFILE_AVATAR_YANDEX_12": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_12.png",
        "IDR_PROFILE_AVATAR_YANDEX_13": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_13.png",
        "IDR_PROFILE_AVATAR_YANDEX_14": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_14.png",
        "IDR_PROFILE_AVATAR_YANDEX_15": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_15.png",
        "IDR_PROFILE_AVATAR_YANDEX_16": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_16.png",
        "IDR_PROFILE_AVATAR_YANDEX_17": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_17.png",
        "IDR_PROFILE_AVATAR_YANDEX_18": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_18.png",
        "IDR_PROFILE_AVATAR_YANDEX_19": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_19.png",
        "IDR_PROFILE_AVATAR_YANDEX_20": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_20.png",
        "IDR_PROFILE_AVATAR_YANDEX_21": ":/images/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_21.png",
    },
}

def path_not_exist(path: str | Path) -> bool:
    """
    判断目标路径是否存在
    如果参数为空或者 None，亦认为不存在

    :param path: 目标路径
    :return:
    """
    if isinstance(path, str):
        return len(path) == 0 or not Path(path).exists()
    elif isinstance(path, Path):
        return not path.exists()
    else:
        return True


def get_with_chained_keys(dic: dict, keys: list, default=None):
    """
    调用 get_with_chained_keys(d, ["a", "b", "c"])
    等同于 d["a"]["b"]["c"] ，
    只不过中间任意一次索引如果找不到键，则返回 default

    :param dic: 目标字典
    :param keys: 键列表
    :param default: 找不到键时的默认返回值
    :return:
    """
    if not isinstance(dic, dict):
        return default
    if len(keys) == 0:
        return default
    k = keys[0]
    if k not in dic:
        return default
    if len(keys) == 1:
        return dic[k]
    return get_with_chained_keys(dic[k], keys[1:], default)


def get_icon_path(icon_name: str, sub_dir: str = None) -> str:
    if sub_dir is None:
        if icon_name not in icons_map:
            icon_name = "none"
        return icons_map[icon_name]
    else:
        p = get_with_chained_keys(icons_map, [sub_dir, icon_name])
        return icons_map["none"] if p is None else p


def accept_warning(widget: QWidget, condition: bool,
                   caption: str = "Warning", text: str = "Are you sure to continue?") -> bool:
    if condition:
        mb = MessageBox(caption, text, widget)
        if not mb.exec():
            return True
    return False


def show_quick_tip(widget: QWidget, caption: str, text: str):
    mb = MessageBox(caption, text, widget)
    mb.cancelButton.setHidden(True)
    mb.buttonLayout.insertStretch(0, 1)
    mb.buttonLayout.setStretch(1, 0)
    mb.yesButton.setMinimumWidth(100)
    mb.setClosableOnMaskClicked(True)
    mb.exec()
