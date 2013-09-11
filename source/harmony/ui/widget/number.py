# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .string import String


class Number(String):
    '''Number input with fraction or exponent part.'''

    DEFAULT_RANGE = (-9999999.99, 9999999.99)

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

        super(Number, self).__init__(**kw)

    def _constructControl(self):
        '''Return the control widget.'''
        control = super(Number, self)._constructControl()
        validator = self._constructValidator()
        if validator:
            control.setValidator(validator)

        return control

    def _constructValidator(self):
        '''Return appropriate validator.'''
        return QtGui.QDoubleValidator(self._minimum, self._maximum, self)

    def value(self):
        '''Return current value.'''
        value = super(Number, self).value()
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def setValue(self, value):
        '''Set current *value*.'''
        if value is not None:
            value = str(value)
        super(Number, self).setValue(value)

