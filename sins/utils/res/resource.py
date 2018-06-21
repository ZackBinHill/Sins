# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/4/2018

import os
import sys
from sins.module.sqt import *
from sins.utils.const import declare_constants
from sins.utils.log import get_logger
useRes = False
try:
    import respy1
    useRes = True
except ImportError:
    pass


logger = get_logger(__name__)

Res_Folder = '/'.join(__file__.replace('\\', '/').split('/')[:-3]) + '/resource'

icon = declare_constants(
    Shot="icon/Shots.png",
    Shot_B="icon/Shots_bright.png",
    Sequence="icon/Sequences.png",
    Sequence_B="icon/Sequences_bright.png",
    Media="icon/Media.png",
    Task="icon/Tasks.png",
    Asset="icon/Assets.png",
    Asset_B="icon/Assets_bright.png",
    File="icon/Files.png",
    Tag="icon/Tags.png",
)


error_pic = declare_constants(
    Error01=os.path.join(Res_Folder, 'other', 'Error01.png'),
    Error02=os.path.join(Res_Folder, 'other', 'Error02.png'),
)


def get_pic(*args):
    if useRes:
        return ":res/" + "/".join(list(args))
    else:
        return os.path.join(Res_Folder, *args).replace('\\', '/')


def get_qicon(*args):
    return QIcon(get_pic(*args))


# def get_pixmap(*args, **kwargs):
#     """
#     return QPixmap object based on name and scale
#     :param name: pic name
#     :param scale: scale factor, list or int
#     :return: QPixmap
#     """
#     if "scale" not in kwargs:
#         if os.path.exists(args[0]):
#             return QPixmap(args[0])
#         return QPixmap(get_pic(*args))
#     else:
#         scale = kwargs["scale"]
#         if isinstance(scale, list):
#             if os.path.exists(args[0]):
#                 return QPixmap(args[0]).scaled(scale[0], scale[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
#             return QPixmap(get_pic(*args)).scaled(scale[0], scale[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
#         else:
#             if os.path.exists(args[0]):
#                 return QPixmap(args[0]).scaled(scale, scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)
#             return QPixmap(get_pic(*args)).scaled(scale, scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def get_pixmap(*args, **kwargs):
    """
    return QPixmap object based on name and scale
    :param name: pic name
    :param scale: scale factor, list or int
    :return: QPixmap
    """
    path = args[0] if os.path.isfile(args[0]) else get_pic(*args)
    scale = kwargs.get('scale')
    aspect = kwargs.get('aspect', 'keep')
    color = kwargs.get('color')
    error = kwargs.get('error', 'Error01')

    if isinstance(scale, QSize):
        pass
    elif isinstance(scale, (list, tuple)):
        scale = QSize(scale[0], scale[1])
    elif isinstance(scale, int):
        scale = QSize(scale, scale)

    if isinstance(color, QColor):
        pass
    elif color == "auto":
        color = QApplication.palette().text().color()
    elif isinstance(color, basestring):
        color = QColor(color)
    elif isinstance(color, int):
        color = QColor(color)
    elif isinstance(color, list):
        color = QColor(color[0], color[1], color[2])
    elif isinstance(color, QWidget):
        widget = color
        is_enabled = widget.isEnabled()
        if not is_enabled:
            widget.setEnabled(True)
        color = widget.palette().text().color()
        if not is_enabled:
            widget.setEnabled(is_enabled)

    if path.endswith("svg"):
        svg = QtSvg.QSvgRenderer(path)
        if not scale:
            scale = svg.defaultSize()

        img = QImage(scale, QImage.Format_ARGB32)
        painter = QPainter()
        painter.begin(img)

        if not color:
            color = QApplication.palette().text().color()

        if color:
            painter.setCompositionMode(QPainter.CompositionMode_Plus)
            painter.fillRect(img.rect(), color)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOut)
        svg.render(painter)
        if color:
            painter.fillRect(img.rect(), color)
        painter.end()
        pixmap = QPixmap.fromImage(img)

    else:
        img = QImage(path)
        if img.width() == 0:
            logger.warning('error image: "{}"'.format(path))
            img = QImage(getattr(error_pic, error))
        if scale:
            if aspect == 'keep':
                img = img.scaled(scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            elif aspect == 'expand':
                img = img.scaled(scale, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            elif aspect == 'width':
                img = img.scaledToWidth(scale.width(), Qt.SmoothTransformation)
            elif aspect == 'height':
                img = img.scaledToHeight(scale.height(), Qt.SmoothTransformation)
        if color:
            img = img.convertToFormat(QImage.Format_Indexed8)
            if img.depth() in [1, 8]:
                for index in range(img.colorCount()):
                    src_color = QColor.fromRgba(img.color(index))
                    img.setColor(index, QColor(color.red(), color.green(), color.blue(),
                                                     src_color.alpha()).rgba())
            else:
                for row in range(img.height()):
                    # print img.scanLine(row)
                    # print len(img.scanLine(row))
                    # help(img.scanLine(row))
                    # for pix in img.scanLine(row):
                    #     print pix
                    for col in range(img.width()):
                        src_color = QColor.fromRgba(img.pixel(col, row))
                        if not src_color.alpha():
                            continue
                        img.setPixel(col, row, color.rgb())

        pixmap = QPixmap.fromImage(img)

    return pixmap


def get_style(name):
    if useRes:
        cssFile = QFile(":res/style/%s.css" % name)
        cssFile.open(QFile.ReadOnly)
        css = cssFile.readAll().data()
        cssFile.close()
        css = css.replace("%s", ":res")
        return css
    else:
        styleFile = os.path.join(Res_Folder, "style", "%s.css" % name)
        styleText = open(styleFile).read()
        styleText = styleText.replace("%s", Res_Folder)
        styleText = styleText.replace("\\", "/")
        # print styleText
        return styleText


def get_qmovie(*args):
    return QMovie(get_pic(*args))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # print get_pic("player", "aaa.png")
    # print get_pixmap("player", "aaa.png")
    print get_pixmap('F:/Temp/pycharm/Sins_data/sins/File/0000/0000/0015/DRM.jpg', scale=[100, 70])
    # print get_style("main_gui")
    app.exec_()
