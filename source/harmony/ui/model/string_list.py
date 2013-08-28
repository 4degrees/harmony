# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore

from . import HARMONY_DATA_ROLE


class StringList(QtGui.QStringListModel):
    '''Manage a list of strings.'''

    def data(self, index, role):
        '''Return data for *role* at *index*.'''
        if role == HARMONY_DATA_ROLE:
            role = QtCore.Qt.DisplayRole

        return super(StringList, self).data(index, role)

    def match(self, start, role, value, hits=1, flags=None):
        '''Return indexes that match *value* for *role*.'''
        if role == HARMONY_DATA_ROLE:
            role = QtCore.Qt.DisplayRole

        return super(StringList, self).match(
            start, role, value, hits, flags
        )

