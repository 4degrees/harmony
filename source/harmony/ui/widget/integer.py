# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .simple import Simple


class Integer(Simple):
    '''Number input without fraction or exponent part.'''

    DEFAULT_RANGE = (-9999999, 9999999)

    def __init__(self, minimum=None, maximum=None, **kw):
        '''Initialise widget.

        *minimum* is the minimum value that can be selected.
        *maximum* is the maximum value that can be selected.

        '''
        super(Integer, self).__init__(minimum=minimum, maximum=maximum, **kw)

    def _constructControl(self, minimum, maximum, **kw):
        '''Return the control widget.

        Subclasses should override this to return an appropriate control
        widget.

        '''
        control = QtGui.QSpinBox()

        if minimum is None:
            minimum = self.DEFAULT_RANGE[0]

        control.setMinimum(minimum)

        if maximum is None:
            maximum = self.DEFAULT_RANGE[1]

        control.setMaximum(maximum)

        return control

    def _postConstruction(self, **kw):
        '''Perform post-construction operations.'''
        super(Integer, self)._postConstruction(**kw)
        self._control.valueChanged.connect(self._emitValueChanged)

    def value(self):
        '''Return current value.'''
        return self._control.value()

    def setValue(self, value):
        '''Set current *value*.'''
        self._control.setValue(value)
