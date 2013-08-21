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

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(String, self).setTitle(value)

        placeholder = self._title
        if not self.required():
            placeholder += ' (optional)'

        self._control.setPlaceholderText(placeholder)

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        super(String, self).setRequired(value)
        self.setTitle(self.title())

    def value(self):
        '''Return current value.'''
        return self._control.text()

    def setValue(self, value):
        '''Set current *value*.'''
        self._control.setText(value)
