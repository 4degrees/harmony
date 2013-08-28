# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from ..model import HARMONY_DATA_ROLE
from ..model.placeholder_proxy_model import PlaceholderProxyModel
from .simple import Simple


class Enum(Simple):
    '''Enumerated string option.'''

    def __init__(self, model, **kw):
        '''Initialise widget.

        *model* provides the data to populate the selector. It will be proxied
        via a PlaceholderProxyModel that transparently manages an initial
        placeholder item.

        '''
        self._model = PlaceholderProxyModel(model)
        super(Enum, self).__init__(**kw)

    def _constructControl(self):
        '''Return the control widget.

        '''
        control = QtGui.QComboBox()
        control.setModel(self._model)
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

        return self._control.itemData(
            self._control.currentIndex(), role=HARMONY_DATA_ROLE
        )

    def setValue(self, value):
        '''Set current *value*.'''
        if value is None:
            index = 0
        else:
            index = self._control.findData(value, role=HARMONY_DATA_ROLE)
            if index == -1:
                index = 0

        self._control.setCurrentIndex(index)

