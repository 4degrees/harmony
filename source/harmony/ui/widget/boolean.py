# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .simple import Simple


class Boolean(Simple):
    '''Boolean control.'''

    def _construct(self):
        '''Construct widget.'''
        super(Boolean, self)._construct()
        self.layout().setStretchFactor(self._control, 0)
        self.layout().addStretch(1)

    def _constructControl(self):
        '''Return the control widget.'''
        return QtGui.QCheckBox()

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        super(Boolean, self)._postConstruction()
        self._control.stateChanged.connect(self._emitValueChanged)

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(Boolean, self).setTitle(value)
        self._control.setText(self._title)

    def value(self):
        '''Return current value.'''
        return self._control.isChecked()

    def setValue(self, value):
        '''Set current *value*.'''
        self._control.setChecked(value)

