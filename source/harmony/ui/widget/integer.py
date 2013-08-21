# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .string import String


class Integer(String):
    '''Number input without fraction or exponent part.'''

    DEFAULT_RANGE = (-9999999, 9999999)

    def __init__(self, minimum=None, maximum=None, **kw):
        '''Initialise widget.

        *minimum* is the minimum value that can be selected.
        *maximum* is the maximum value that can be selected.

        '''
        self._minimum = minimum
        if self._minimum is None:
            self._minimum = self.DEFAULT_RANGE[0]

        self._maximum = maximum
        if self._maximum is None:
            self._maximum = self.DEFAULT_RANGE[1]

        super(Integer, self).__init__(**kw)

    def _constructControl(self):
        '''Return the control widget.'''
        control = super(Integer, self)._constructControl()
        control.setValidator(
            QtGui.QIntValidator(self._minimum, self._maximum, self)
        )

        return control

    def value(self):
        '''Return current value.'''
        value = super(Integer, self).value()
        try:
            return int(value)
        except ValueError:
            return None

    def setValue(self, value):
        '''Set current *value*.'''
        super(Integer, self).setValue(str(value))
