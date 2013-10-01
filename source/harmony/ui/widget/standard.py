# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore

from .base import Widget


class Standard(Widget):
    '''Standard widget that wraps a single control.'''

    def _construct(self):
        '''Construct widget.'''
        super(Standard, self)._construct()
        self.setLayout(QtGui.QVBoxLayout())

        self._titleLabel = QtGui.QLabel()
        self._titleLabel.setFixedWidth(80)
        self._titleLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )

        self._headerLayout = QtGui.QHBoxLayout()
        self._headerLayout.addWidget(self._titleLabel, stretch=0)
        self._headerLayout.addWidget(self._errorIndicator, stretch=0)
        self._headerLayout.setContentsMargins(0, 0, 0, 0)

        self.layout().addLayout(self._headerLayout, stretch=0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(Standard, self).setTitle(value)

        title = self._title
        if self.required():
            title += '*'

        self._titleLabel.setText(title)

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        super(Standard, self).setRequired(value)
        self.setTitle(self.title())

    def setDescription(self, value):
        '''Set description to *value*.'''
        super(Standard, self).setDescription(value)
        self._titleLabel.setToolTip(self._description)
