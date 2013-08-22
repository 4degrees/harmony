# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .simple import Simple


class String(Simple):
    '''Single line text based input.'''

    def _constructControl(self):
        '''Return the control widget.'''
        control = QtGui.QLineEdit()
        return control

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        super(String, self)._postConstruction()
        self._control.textChanged.connect(self._emitValueChanged)

    def value(self):
        '''Return current value.'''
        value = self._control.text()
        value = value.strip()
        if not value:
            value = None

        return value

    def setValue(self, value):
        '''Set current *value*.'''
        self._control.setText(value)

