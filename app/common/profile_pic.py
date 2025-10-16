from PySide6.QtGui import QIcon

from app.common.icons import get_icon_from_svg

# ChatGPT 生成
# 十六进制颜色里不能有 alpha 通道，否则绘制不出来
profile_svg = """
<svg version="1.1" width="96" height="96" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
  <circle cx="48" cy="48" r="48" fill="#{bg_rgb}"/>
  <g fill="#{fg_rgb}">
    <circle cx="48" cy="32" r="12"/>
    <path d="M24,68 C20,50 40,48 48,48 C56,48 76,50 72,68 Z"/>
  </g>
</svg>
"""

profile_icon_map: dict[tuple[int, int], QIcon] = {}


def argb_to_rgb(argb_value: int) -> int:
    # 提取 ARGB 各个部分
    # alpha = (argb_value >> 24) & 0xFF
    red = (argb_value >> 16) & 0xFF
    green = (argb_value >> 8) & 0xFF
    blue = argb_value & 0xFF

    # 重新排列为 RGB 格式
    rgba_value = (red << 16) | (green << 8) | blue

    return rgba_value


def create_profile_pic(bg_rgba: int, fg_rgba: int) -> QIcon:
    if (bg_rgba, fg_rgba) in profile_icon_map:
        return profile_icon_map[(bg_rgba, fg_rgba)]

    bg = format(argb_to_rgb(4294967296 + bg_rgba), "x")
    fg = format(argb_to_rgb(4294967296 + fg_rgba), "x")
    icon = get_icon_from_svg(profile_svg.format(bg_rgb=bg, fg_rgb=fg), 96, 96)
    profile_icon_map[(bg_rgba, fg_rgba)] = icon

    return icon
