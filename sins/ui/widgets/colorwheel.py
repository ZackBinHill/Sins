# this file is modified based on
# https://code.google.com/p/dedafx-dev/source/browse/trunk/python/gui/qt/ColorWheel.py?r=3


import sys
import math
from sins.module.sqt import *
from sins.utils.color import int10_to_rgb


def clamp(value, min=0.0, max=1.0):
    if value > max:
        return max
    elif value < min:
        return min
    else:
        return value


class ColorWheelWidget(QWidget):
    colorSignal = Signal(list)

    def __init__(self, parent=None):
        super(ColorWheelWidget, self).__init__(parent)

        # self.setStyleSheet('background:rgb(50, 50, 50)')

        self.dim = 150
        self.offset = 10
        self.colorWheelSensitivity = 0.1
        self.master_radius = (self.dim / 2) + self.offset + 5
        self.center = (self.master_radius, self.master_radius)
        self.centerPoint = QPointF(self.master_radius, self.master_radius)
        self.valueAngle = 360
        self.huepoint = (self.master_radius, self.master_radius)

        self.guiSelection = 0  # 0:hue,sat 1:lum
        self.valueAngleSat = 0
        self.mousePressed = False

        self.color = QColor(255, 255, 255, 255)

        self.init_paint()

    def init_paint(self):
        # the color wheel image, only needs to be generated once
        self.image = QImage(self.master_radius * 2, self.master_radius * 2, QImage.Format_ARGB32)
        self.image.fill(QColor(0, 0, 0, 0).rgba())

        for y in range(int(self.master_radius * 2)):
            for x in range(int(self.master_radius * 2)):
                d = 2 * self.get_dist((x, y), self.center) / self.dim
                if d <= 1:  # Hue Wheel
                    color = QColor()
                    hue = self.get_hue(x, y)
                    percent = max(0, min(1, (d - 0.90) * 30))
                    color.setHsv(hue, (d * 255), 90 + (165 * percent),
                                 90 + (165 * percent))  # The dark part in the center

                    self.image.setPixel(x, y, color.rgba())
                else:
                    d2 = self.get_dist((x, y), self.center) / (self.master_radius - 1)
                    if d2 > 1:  # MainBG
                        color = QColor()
                        color.setAlpha(0)
                        self.image.setPixel(x, y, color.rgba())
                    else:
                        pass

        self.lumGradient = QConicalGradient()
        self.lumGradient.setCenter(self.centerPoint)
        self.lumGradient.setAngle(-90)
        self.lumGradient.setColorAt(1, QColor(255, 255, 255))
        self.lumGradient.setColorAt(0, QColor(20, 20, 20))

        self.lumPen = QPen()
        self.lumPen.setWidth(3)
        self.lumPen.setColor(QColor(150, 150, 150))
        self.lumPen.setBrush(self.lumGradient)

        self.lumRect = QRectF(self.center[0] - ((self.dim * 1.1) / 2),
                              self.center[1] - ((self.dim * 1.1) / 2),
                              self.dim * 1.1,
                              self.dim * 1.1)

        self.outLinePen = QPen(QColor(20, 20, 20))
        self.outLinePen.setWidth(2)

        self.crossPen = QPen(QColor(200, 200, 200))
        self.crossPen.setWidth(1)

        self.guidePen = QPen(QColor(220, 220, 220))
        self.guidePen.setWidth(1.99)
        self.guidePen.setStyle(Qt.DashLine)

        self.hueDotPen = QPen()
        self.hueDotPen.setWidth(1)
        self.hueDotPen.setStyle(Qt.SolidLine)

    def get_dist(self, (x1, y1), (x2, y2)):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

    def get_rot(self, x, y):
        return ( math.degrees ( math.atan2 ( 2*(x - self.master_radius), 2*(y - self.master_radius)))) % 360

    def get_hue(self, x, y):
        return ( math.degrees ( math.atan2 ( 2 * (x - self.master_radius), 2 * (y - self.master_radius))) + 165 ) % 360

    def get_radial_line_points(self, r_inner, r_outer, angle, distance=1.0):
        rad = math.radians(angle)
        sr = math.sin(rad)
        cr = math.cos(rad)
        x1 = r_outer - (r_outer * (sr*distance))
        y1 = r_outer - (r_outer * (cr*distance))
        x2 = r_outer - (r_inner * (sr*distance))
        y2 = r_outer - (r_inner * (cr*distance))
        return (x1, y1, x2, y2)

    def paintEvent(self, evt):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawImage(0, 0, self.image)

        # DRAW THE OUTER BLACK CIRCLE
        painter.setPen(self.outLinePen)
        painter.drawEllipse(self.centerPoint, self.dim / 2, self.dim / 2)

        # LUMINANCE ARC
        painter.setPen(self.lumPen)
        spanAngle = (self.valueAngle) * 16
        painter.drawArc(self.lumRect, -90 * 16, spanAngle)

        # Middle Crosshair
        painter.setPen(self.crossPen)
        painter.drawLine((self.master_radius) + 4, (self.master_radius), (self.master_radius) - 4, (self.master_radius))
        painter.drawLine((self.master_radius), (self.master_radius) + 4, (self.master_radius), (self.master_radius) - 4)

        # Draw the GuideLines
        painter.setPen(self.guidePen)
        (hpx, hpy) = self.huepoint
        d = self.get_dist((hpx, hpy), self.center)
        if self.mousePressed:
            (x1, y1, x2, y2) = self.get_radial_line_points(0, self.master_radius, self.color.hue() + 15, 0.80)
            painter.drawLine(x1, y1, x2, y2)
            if d > 46:  # If the radial is in the bright area, then display a dark version
                self.guidePen.setColor(QColor(20, 20, 20))
                painter.setPen(self.guidePen)
            if d != 0:
                self.guidePen.setColor(QColor(220, 220, 220))
                painter.drawEllipse(QPointF(self.master_radius, self.master_radius), d, d)

        # Draw Hue Dot
        if self.color.value() > 90:
            self.hueDotPen.setColor(QColor(0, 0, 0))
        else:
            self.hueDotPen.setColor(QColor(220, 220, 220))
        painter.setPen(self.hueDotPen)
        brush = QBrush(QColor(self.color.rgb()))
        painter.setBrush(brush)
        painter.drawEllipse(QPointF(hpx, hpy), 5, 5)

    def alter_color(self, x, y):
        d = 2.0 * self.get_dist((x, y), self.center) / self.dim
        if self.guiSelection == 0:
            if self.get_dist((x, y), self.center) >= (self.dim / 2.0):
                Percent = self.get_dist((x, y), self.center) / (self.dim / 2.0)
                prex = (((x - self.center[0]) / Percent) * 1) + self.center[0]
                prey = (((y - self.center[1]) / Percent) * 1) + self.center[1]
                x = prex
                y = prey
            hue = self.get_hue(x, y)

            self.valueAngleSat = (1.0 - ((self.get_dist((x, y), self.center) / (self.dim / 2.0)) * 90.0)) + 135.0
            self.huepoint = (x, y)
            self.set_hsv(hue, min(d * 255.0, 255.0), self.color.value())

        elif self.guiSelection == 1:
            self.valueAngle = self.get_rot(x, y)
            v = (self.valueAngle / 360.0) * 255.0
            self.set_hsv(self.color.hue(), self.color.saturation(), v)
        else:
            pass

    def set_hsv(self, h, s, v):
        self.color.setHsvF(clamp(h / 360.0), clamp(s / 255.0), clamp(v / 255.0))
        # print self.color.hue(), self.color.saturation(), self.color.value()
        self.update()

    def set_ui_hsv(self, h, s, v):
        (x1, y1, x2, y2) = self.get_radial_line_points((self.dim / 2.0), self.master_radius, h + 15, s / 255.0)
        self.huepoint = (x2, y2)
        #Saturation
        self.valueAngleSat = (1.0-((s / 255.0) * 90.0)) + 135.0
        #Luminance
        self.valueAngle = ((v / 255.0) * 360.0)

    def set_color(self, color, rgb=True):
        if isinstance(color, QColor):
            self.set_hsv(color.hue(), color.saturation(), color.value())
            self.set_ui_hsv(color.hue(), color.saturation(), color.value())
        elif isinstance(color, list):
            if rgb:
                color = QColor(color[0], color[1], color[2])
                self.set_hsv(color.hue(), color.saturation(), color.value())
                self.set_ui_hsv(color.hue(), color.saturation(), color.value())
            else:
                self.set_hsv(color[0], color[1], color[2])
                self.set_ui_hsv(color[0], color[1], color[2])
        elif isinstance(color, (int, long)):
            color = QColor(color)
            # print color.hue(), color.saturation(), color.value(), color.alpha()
            self.set_hsv(color.hue(), color.saturation(), color.value())
            self.set_ui_hsv(color.hue(), color.saturation(), color.value())

    def mousePressEvent(self, evt):
        self.mousePressed = True
        d = 2 * self.get_dist((evt.x(), evt.y()), self.center) / self.dim
        if d <= 1:
            self.guiSelection = 0
            self.alter_color(evt.x(), evt.y())
        else:
            d = self.get_dist((evt.x(), evt.y()), self.center) / self.master_radius
            if d <= 1:
                self.guiSelection = 1
                self.alter_color(evt.x(), evt.y())
            else:
                self.guiSelection = 2

    def mouseMoveEvent(self, evt):
        self.alter_color(evt.x(), evt.y())

    def mouseReleaseEvent(self, QMouseEvent):
        super(ColorWheelWidget, self).mouseReleaseEvent(QMouseEvent)
        self.mousePressed = False
        self.update()


class ColorWheelWindow(QWidget):
    applyColor = Signal()
    def __init__(self, *args, **kwargs):
        super(ColorWheelWindow, self).__init__(*args, **kwargs)

        self.setWindowFlags(Qt.Popup)
        self.setStyleSheet("""
        QWidget{
            background:rgb(50, 50, 50)
        }
        QPushButton{
            border:none;
            color: rgb(220, 220, 220);
            background:rgb(50, 110, 150);
            width:50px;
            height:30px;
        }
        QPushButton:hover{
            background:rgb(50, 100, 140);
        }
        QPushButton:pressed{
            background:rgb(40, 90, 130);
        }
        """)

        self.colorWheel = ColorWheelWidget(self)
        self.applyButton = QPushButton('Apply')
        self.cancelButton = QPushButton('Cancel')

        self.masterLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.masterLayout.addWidget(self.colorWheel)
        self.masterLayout.addLayout(self.buttonLayout)
        self.setLayout(self.masterLayout)

        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)

        self.resize(205, 250)

    def set_color(self, color):
        self.colorWheel.set_color(color)

    def apply_clicked(self):
        # print self.colorWheel.color.rgba(), self.colorWheel.color.red(), self.colorWheel.color.green(), self.colorWheel.color.blue()
        self.applyColor.emit()
        self.close()

    def cancel_clicked(self):
        self.close()


def main(args):
    app=QApplication(args)
    win=ColorWheelWindow()
    win.set_color(4288256383)
    win.show()
    app.exec_()


if __name__=="__main__":
    main(sys.argv)