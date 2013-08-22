# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore

from .base import Widget


class Simple(Widget):
    '''Simple widget that wraps a single control.'''

    def _construct(self):
        '''Construct widget.'''
        super(Simple, self)._construct()
        self.setLayout(QtGui.QHBoxLayout())

        self._titleLabel = QtGui.QLabel()
        self._titleLabel.setFixedWidth(80)
        self._titleLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self._control = self._constructControl()

        self.layout().addWidget(self._titleLabel)
        self.layout().addWidget(self._control, stretch=1)
        self.layout().addWidget(self._errorIndicator)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def _constructControl(self):
        '''Return the control widget.

        Subclasses should override this to return an appropriate control
        widget.

        '''
        raise NotImplementedError()

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(Simple, self).setTitle(value)

        title = self._title
        if self.required():
            title += '*'

        self._titleLabel.setText(title)

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        super(Simple, self).setRequired(value)
        self.setTitle(self.title())

    def setDescription(self, value):
        '''Set description to *value*.'''
        super(Simple, self).setDescription(value)
        self._titleLabel.setToolTip(self._description)

    def value(self):
        '''Return current value.'''
        raise NotImplementedError()

    def setValue(self, value):
        '''Set current *value*.'''
        raise NotImplementedError()
