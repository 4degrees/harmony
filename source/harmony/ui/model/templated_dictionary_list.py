# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtCore

from . import HARMONY_DATA_ROLE


class TemplatedDictionaryList(QtCore.QAbstractListModel):
    '''Manage a list of dictionaries and display as strings.'''

    def __init__(self, template, items=None, parent=None):
        '''Initialise model.

        *template* is the template to use to format the data when returning
        a DisplayRole value. It can be any callable that has a `format`
        function. The format function should follow the signature of the
        standard Python string format function.

        *items* is a list of dictionaries to populate the model with initially.

        *parent* should be the owner of this model.

        '''
        self.template = template
        self._items = items
        if self._items is None:
            self._items = []

        super(TemplatedDictionaryList, self).__init__(parent=parent)

    def rowCount(self, parent=None):
        '''Return a count of the number of rows in the model.'''
        return len(self._items)

    def clear(self):
        '''Remove all items from model.'''
        self.beginResetModel()
        del self._items[:]
        self.endResetModel()

    def setItems(self, items):
        '''Set current *items* clearing any existing ones.'''
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def data(self, index, role):
        '''Return data for *role* at *index*.

        If role is DisplayRole then use the initialised template to format the
        data found by accessing the same index with the HARMONY_DATA_ROLE.

        '''
        value = None

        if role == QtCore.Qt.DisplayRole:
            data = self.data(index, HARMONY_DATA_ROLE)
            if data is not None:
                value = self.template.format(**data)

        elif role == HARMONY_DATA_ROLE:
            try:
                value = self._items[index.row()]
            except IndexError:
                return None

        return value

    def match(self, start, role, value, hits=1, flags=None):
        '''Return indexes that match *value* for *role*.'''
        if role == HARMONY_DATA_ROLE:
            matches = []

            start_row = 0
            if start.isValid():
                start_row = start.row()

            for row in range(start_row, self.rowCount()):
                index = self.index(row, 0)
                data = self.data(index, role)
                if data == value:
                    matches.append(index)

                if len(matches) >= hits:
                    break

            return matches

        else:
            return super(TemplatedDictionaryList, self).match(
                start, role, value, hits, flags
            )

