# -*- coding: utf-8 -*-

from BQt import QtGui, QtCore, QtWidgets
from bfx.ui.version_graph.utils import open_version_in_browser, open_version_in_file_explorer
from bfx.ui.util import get_pipeline_color
from bfx.util.log import log_time_cost
from bfx.data.ple.assets import Entity, Asset
import time


SPECIAL_COLOR = {
    'cc_bundle': [[200, 80, 80], [115, 115, 255]]
}


class Label(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)

    def paintEvent(self, qpaintevent):
        painter = QtGui.QPainter(self)
        font = painter.font()
        fm = QtGui.QFontMetrics(font)
        w = fm.boundingRect(self.text()).width() + 10
        h = fm.boundingRect(self.text()).height()
        painter.setFont(font)
        # painter.setPen(QtGui.QPen(QtGui.QColor(10, 10, 10)))
        painter.drawText(0, 0, w, h, 0, self.text())
        super(Label, self).paintEvent(qpaintevent)


class VersionItemWidget(QtWidgets.QWidget):

    def __init__(self, version, entity, asset, **kwargs):
        super(VersionItemWidget, self).__init__(**kwargs)

        self.version = version
        self.entity = entity
        self.asset = asset
        self.layout1 = QtWidgets.QHBoxLayout()
        self.version_label = Label()
        self.version_label.setStyleSheet('font: italic bold 17px Arial')
        self.color_label = QtWidgets.QLabel()
        self.step_label = Label()
        self.step_label.setStyleSheet('font: bold 17px Arial')
        self.layout1.addWidget(self.version_label)
        self.layout1.addStretch()
        self.layout1.addWidget(self.color_label)
        self.layout1.addWidget(self.step_label)
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.masterLayout = QtWidgets.QVBoxLayout()
        self.masterLayout.addSpacing(5)
        self.masterLayout.addLayout(self.layout1)
        self.masterLayout.addStretch()
        self.masterLayout.addLayout(self.form_layout)
        self.setLayout(self.masterLayout)
        self.masterLayout.setAlignment(QtCore.Qt.AlignTop)
        self.masterLayout.setContentsMargins(10, 0, 0, 5)
        #
        self.version_label.setText(self.version.name)
        self.color_label.setFixedSize(QtCore.QSize(20, 20))
        self.tooltip_text = None
        basset_name = Label('BAsset:')
        # basset_label = Label(self.exporter.basset_url.asset.name)
        basset_label = Label(self.asset.name)
        entity_name = Label('Entity:')
        entity_label = Label(self.entity.get_full_name())
        for label in [basset_name, entity_name, basset_label, entity_label]:
            # label.setStyleSheet('font: 12px Liberation Sans')
            # label.setStyleSheet('font: 12px Bitstream Vera Sans')
            label.setStyleSheet('font: 12px DejaVu Sans')
        self.form_layout.addRow(basset_name, basset_label)
        self.form_layout.addRow(entity_name, entity_label)
        if self.entity.type == 'step':
            self.step_label.setText(self.entity.name)

        style = """
        *{
            background: transparent;
            color: rgb(220, 220, 220);
        }
        QToolTip{
            color:white;
        }
        """
        self.setStyleSheet(style)
        self.is_highlight = False

        self.resize(200, 80)
        # self.backLabel.setFixedSize(self.width(), self.height())

    def set_highlight(self, value=True):
        if self.is_highlight != value:
            if value:
                self.setStyleSheet('*{color: rgb(40, 40, 40);background: transparent;}')
            else:
                self.setStyleSheet('*{color: rgb(220, 220, 220);background: transparent;}')
            self.is_highlight = value

    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            if self.tooltip_text is None:
                self.tooltip_text = u'id: {id}\ndate: {date}\nby: {create_by}\nnotes: {notes}'.\
                    format(id=self.version.id,
                           date=self.version.date_published,
                           create_by=self.version.creator.username,
                           notes=self.version.notes
                           )
                # print self.tooltip_text
            QtWidgets.QToolTip.showText(QtGui.QCursor().pos(), self.tooltip_text)
            return True
        return super(VersionItemWidget, self).event(event)

    @classmethod
    def create_item(cls, version, entity, asset, *args, **kwargs):
        if entity.name == 'pla':
            item = PlaVersionItemWidget(version, entity, asset, *args, **kwargs)
        else:
            item = VersionItemWidget(version, entity, asset, *args, **kwargs)
        return item


class PlaVersionItemWidget(VersionItemWidget):
    def __init__(self, *args, **kwargs):
        super(PlaVersionItemWidget, self).__init__(*args, **kwargs)

        if self.asset.name == 'cc_bundle':
            self.step_label.setText('cc_bundle')
        else:
            pass




