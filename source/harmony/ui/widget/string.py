# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .simple import Simple


class String(Simple):
    '''Single line text based input.'''

    def _constructControl(self, **kw):
        '''Return the control widget.

        Subclasses should override this to return an appropriate control
        widget.

        '''
        return QtGui.QLineEdit()

    def _postConstruction(self, **kw):
        '''Perform post-construction operations.'''
        super(String, self)._postConstruction(**kw)
        self._control.textChanged.connect(self._emitValueChanged)

    def value(self):
        '''Return current value.'''
        return self._control.text()

    def setValue(self, value):
        '''Set current *value*.'''
        self._control.setText(value)
