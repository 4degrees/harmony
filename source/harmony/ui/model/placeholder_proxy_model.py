# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore


class PlaceholderProxyModel(QtGui.QProxyModel):
    '''Transparently manage a placeholder as first item in model.'''

    def __init__(self, model=None, placeholder='Select', *args, **kw):
        '''Initialise proxy model with a *placeholder*.'''
        self._placeholder = placeholder
        self._offset = 2
        super(PlaceholderProxyModel, self).__init__(*args, **kw)
        if model is not None:
            self.setModel(model)

    def rowCount(self, parent=None):
        '''Return row count.'''
        if self.model():
            return (self.model().rowCount() + self._offset)
        else:
            return self._offset

    def index(self, row, column, parent=None):
        '''Return an index for *row*, *column* and *parent*.'''
        return self.createIndex(row, column)

    def mapToSource(self, index):
        '''Map *index* to correct source model *index*.'''
        return self.index(
            index.row() - self._offset, index.column(), index.parent()
        )

    def data(self, index, role):
        '''Return data for *index* and *role*.

        The placeholder is at row 0 and can be accessed using the DisplayRole.
        The separator is at row 1.

        '''
        if index.row() == 0:
            if role == QtCore.Qt.DisplayRole:
                return self._placeholder
            else:
                return None

        if index.row() == 1:
            if role == QtCore.Qt.AccessibleDescriptionRole:
                return 'separator'
            else:
                return None

        return super(PlaceholderProxyModel, self).data(
            self.mapToSource(index), role=role
        )

    def setData(self, index, value, role):
        '''Set data for *role* at *index* to *value*.

        The placeholder is at row 0 and can be altered using the EditRole.
        The separator is at row 1 and cannot be altered.

        '''
        if index.row() == 0:
            if role == QtCore.Qt.EditRole:
                self._placeholder = value
                return True
            else:
                return False

        elif index.row() == 1:
            if role in (QtCore.Qt.AccessibleDescriptionRole,
                        QtCore.Qt.EditRole):
                return True
            else:
                return False

        else:
            return super(PlaceholderProxyModel, self).setData(
                self.mapToSource(index), value, role
            )

