# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .simple import Simple


class Enum(Simple):
    '''Enumerated string option.'''

    def __init__(self, items=None, **kw):
        '''Initialise widget.

        *items* should be a list of strings in order that are valid choices
        for the enum.

        '''
        super(Enum, self).__init__(items=items, **kw)

    def _constructControl(self, items, **kw):
        '''Return the control widget.

        '''
        control = QtGui.QComboBox()
        control.addItems(items)

        return control

    def _postConstruction(self, **kw):
        '''Perform post-construction operations.'''
        super(Enum, self)._postConstruction(**kw)
        self._control.currentIndexChanged.connect(self._emitValueChanged)

    def value(self):
        '''Return current value.'''
        return self._control.itemText(self._control.currentIndex())

    def setValue(self, value):
        '''Set current *value*.'''
        index = self._control.findText(value)
        self._control.setCurrentIndex(index)

