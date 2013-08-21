# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .base import Widget


class Simple(Widget):
    '''Simple widget that wraps a single control.'''

    def _construct(self):
        '''Construct widget.'''
        super(Simple, self)._construct()
        self.setLayout(QtGui.QHBoxLayout())

        self._control = self._constructControl()

        self.layout().addWidget(self._control, stretch=1)
        self.layout().addWidget(self._errorIndicator)

    def _constructControl(self):
        '''Return the control widget.

        Subclasses should override this to return an appropriate control
        widget.

        '''
        raise NotImplementedError()

    def setDescription(self, value):
        '''Set description to *value*.'''
        super(Simple, self).setDescription(value)
        self._control.setToolTip(self._description)

    def value(self):
        '''Return current value.'''
        raise NotImplementedError()

    def setValue(self, value):
        '''Set current *value*.'''
        raise NotImplementedError()
