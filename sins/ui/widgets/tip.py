# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/23/2018

from sins.module.sqt import *


class ToastWidget(QLabel):
    DEFAULT_DURATION = 1000

    # FOREGROUND_COLOR = QColor(255, 255, 255)
    # BACKGROUND_COLOR = QColor(0, 0, 0)

    def __init__(self, parent=None, fc=(255, 255, 255), bc=(0, 0, 0), *args):
        QLabel.__init__(self, parent, *args)

        self.__style()

        self.fg_color = QColor(fc[0], fc[1], fc[2])
        self.bg_color = QColor(bc[0], bc[1], bc[2])

        self._messageDisplayTimer = QTimer(self)
        self._messageDisplayTimer.timeout.connect(self.fadeOut)

        self._messageFadeOutTimer = QTimer(self)
        self._messageFadeOutTimer.timeout.connect(self._fadeOut)

    def __style(self):
        font = QFont()
        font.setBold(True)
        # font.setPointSize(11)
        self.setFont(font)

        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._alpha = 255

    def alignTo(self, widget, padding=30):
        width = self.textWidth() + padding
        height = self.textHeight() + padding
        x = (widget.width() - width) / 2
        y = (widget.height() - height) / 2

        self.setGeometry(x, y, width, height)

    def textRect(self):
        text = self.text()
        font = self.font()
        metrics = QFontMetricsF(font)
        return metrics.boundingRect(text)

    def textWidth(self):
        textWidth = self.textRect().width()
        return max(0, textWidth)

    def textHeight(self):
        textHeight = self.textRect().height()
        return max(0, textHeight)

    def fadeOut(self):
        self._messageFadeOutTimer.start(5)

    def _fadeOut(self):
        alpha = self.alpha()
        if alpha > 0:
            alpha -= 2
            self.setAlpha(alpha)
        else:
            self.hide()
            self._messageFadeOutTimer.stop()
            self._messageDisplayTimer.stop()

    def setText(self, text, duration=None):
        QLabel.setText(self, text)
        duration = duration or self.DEFAULT_DURATION
        self.setAlpha(255)
        if self.parent():
            self.alignTo(self.parent())
        self._messageDisplayTimer.stop()
        self._messageDisplayTimer.start(duration)

    def showText(self, text, duration=None):
        self.setText(text, duration)
        self.show()
        self.update()
        self.repaint()

    def alpha(self):
        return float(self._alpha)

    def setAlpha(self, value):
        if value < 0:
            value = 0

        textAlpha = value
        backgroundAlpha = value * 0.8

        color = self.fg_color
        backgroundColor = self.bg_color

        color = Color.fromColor(color)
        color.setAlpha(textAlpha)
        backgroundColor = Color.fromColor(backgroundColor)
        backgroundColor.setAlpha(backgroundAlpha)
        self.setStyleSheet('color: {0}; background-color: {1};'.format(color.toString(), backgroundColor.toString()))
        self._alpha = value


class Color(QColor):
    @classmethod
    def fromColor(cls, color):
        color = 'rgb(%d, %d, %d, %d)' % color.getRgb()
        return cls.fromString(color)

    @classmethod
    def fromString(cls, text):
        a = 255
        try:
            r, g, b, a = text.replace('rgb(', '').replace(')', '').split(',')
        except ValueError:
            r, g, b = text.replace('rgb(', '').replace(')', '').split(',')

        return cls(int(r), int(g), int(b), int(a))

    def __eq__(self, other):
        if other == self:
            return True
        elif isinstance(other, Color):
            return self.toString() == other.toString()
        else:
            return False

    def toString(self):
        return 'rgb(%d, %d, %d, %d)' % self.getRgb()

    def isDark(self):
        return self.red() < 125 and self.green() < 125 and self.blue() < 125
