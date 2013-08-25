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
        self._items = items
        if self._items is None:
            self._items = []
        super(Enum, self).__init__(**kw)

    def _constructControl(self):
        '''Return the control widget.

        '''
        control = QtGui.QComboBox()
        control.addItem('Select')  # Title
        control.addItems(self._items)
        control.insertSeparator(1)

        return control

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        super(Enum, self)._postConstruction()
        self._control.currentIndexChanged.connect(self._emitValueChanged)

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(Enum, self).setTitle(value)

        placeholder = 'Select {0}'.format(self._title)
        if not self.required():
            placeholder += ' (optional)'

        self._control.setItemText(0, placeholder)

    def value(self):
        '''Return current value.'''
        if self._control.currentIndex() == 0:
            return None

        return self._control.itemText(self._control.currentIndex())

    def setValue(self, value):
        '''Set current *value*.'''
        if value is None:
            index = 0
        else:
            index = self._control.findText(value)
            if index == -1:
                index = 0

        self._control.setCurrentIndex(index)

