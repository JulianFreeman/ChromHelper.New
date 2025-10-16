from typing import Literal

from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QBrush, QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


def argb32_to_rgb(argb32: int):
    return argb32 & 0x00FFFFFF


def get_icon_from_svg(svg_data: str, w: int = None, h: int = None) -> QIcon:
    w = 128 if w is None else w
    h = 128 if h is None else h

    renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
    pixmap = QPixmap(w, h)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


def create_mono_icon(
        color: str | int | Qt.GlobalColor,
        shape: Literal["rect", "round"],
        size: int = 96) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.PenStyle.NoPen)
    if shape == "rect":
        painter.drawRect(0, 0, size, size)
    else:
        painter.drawEllipse(0, 0, size, size)
    painter.end()

    return QIcon(pixmap)


def create_round_icon_from_pixmap(pixmap: QPixmap, size: int = None):
    if size is None:
        # 创建一个和输入图片大小一样的 QPixmap，带透明背景
        size = min(pixmap.width(), pixmap.height())  # 取最小边长来保证是正方形

    rounded_pixmap = QPixmap(size, size)
    rounded_pixmap.fill(Qt.GlobalColor.transparent)  # 填充为透明背景

    # 使用 QPainter 绘制圆形
    painter = QPainter(rounded_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 创建一个圆形遮罩
    brush = QBrush(pixmap)
    painter.setBrush(brush)
    painter.setPen(Qt.PenStyle.NoPen)

    # 绘制一个圆形区域
    painter.drawEllipse(0, 0, size, size)

    painter.end()

    # 将圆形图像转换为 QIcon
    return QIcon(rounded_pixmap)
