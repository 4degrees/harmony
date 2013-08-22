# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .number import Number


class Integer(Number):
    '''Number input without fraction or exponent part.'''

    DEFAULT_RANGE = (-9999999, 9999999)

    def _constructValidator(self):
        '''Return appropriate validator.'''
        return QtGui.QIntValidator(self._minimum, self._maximum, self)

    def value(self):
        '''Return current value.'''
        value = super(Integer, self).value()
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

