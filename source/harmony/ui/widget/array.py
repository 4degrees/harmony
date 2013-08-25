# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore

from .base import Widget


class Array(Widget):
    '''Represent a list of items with controls for addition and removal.'''

    def __init__(self, types, additionalType=None, **kw):
        '''Initialise widget with valid *types*.

        *types* should be list of dictionaries. Each dictionary should
        have the following keys:

            * constructor - Required callable to return a widget instance.
            * value - Optional initial value to set on the constructed widget.

        Each index in the types list will direct the type of item to expect
        or create at the same index in the managed list.

        *additionalType* can be a dictionary (as per an entry in *types*) that
        specifies how to handle all additional items.

        '''
        self._types = types
        self._additionalType = additionalType
        super(Array, self).__init__(**kw)

    def _construct(self):
        '''Construct the interface.'''
        super(Array, self)._construct()
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        self.setLineWidth(1)

        self.setLayout(QtGui.QVBoxLayout())

        # Header
        self._header = QtGui.QFrame()
        self._header.setLayout(QtGui.QHBoxLayout())

        self._titleLabel = QtGui.QLabel()
        font = QtGui.QFont(self._titleLabel.font())
        font.setBold(True)
        self._titleLabel.setFont(font)

        self._header.layout().addWidget(self._titleLabel, stretch=0)
        self._header.layout().addStretch(1)
        self._header.layout().addWidget(self._errorIndicator, stretch=0)
        self._header.layout().setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(self._header, stretch=0)

        # Item list
        self._itemList = QtGui.QTableWidget()
        self._itemList.setColumnCount(1)
        self._itemList.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        self._itemList.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection
        )
        self._itemList.setVerticalScrollMode(
            QtGui.QAbstractItemView.ScrollPerPixel
        )
        self._itemList.verticalHeader().hide()
        self._itemList.verticalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents
        )
        self._itemList.horizontalHeader().setStretchLastSection(True)
        self._itemList.horizontalHeader().hide()
        self.layout().addWidget(self._itemList, stretch=1)

        # Footer (item list controls)
        self._footer = QtGui.QFrame()
        self._footer.setLayout(QtGui.QHBoxLayout())
        self._footer.layout().addStretch(1)

        self._addButton = QtGui.QPushButton('Add')
        self._addButton.setToolTip('Add a new item to the list.')
        plusIcon = QtGui.QPixmap(':icon_plus')
        self._addButton.setIcon(plusIcon)
        self._addButton.setIconSize(plusIcon.size())
        self._footer.layout().addWidget(self._addButton)

        self._removeButton = QtGui.QPushButton('Remove')
        self._removeButton.setToolTip('Remove selected items from list.')
        minusIcon = QtGui.QPixmap(':icon_minus')
        self._removeButton.setIcon(minusIcon)
        self._removeButton.setIconSize(minusIcon.size())
        self._footer.layout().addWidget(self._removeButton)

        self._footer.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._footer)

        self.layout().setContentsMargins(5, 5, 5, 5)
        self.setSizePolicy(
               QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        super(Array, self)._postConstruction()

        self._removeButton.setDisabled(True)

        # Connect signals
        self._addButton.clicked.connect(self.onAddButtonClick)
        self._removeButton.clicked.connect(self.onRemoveButtonClick)

        selectionModel = self._itemList.selectionModel()
        selectionModel.selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selected, deselected):
        '''Handle change in selection of items.'''
        selectionModel = self._itemList.selectionModel()
        rows = selectionModel.selectedRows()
        if rows:
            self._removeButton.setEnabled(True)
        else:
            self._removeButton.setEnabled(False)

    def onAddButtonClick(self):
        '''Handle add button click.'''
        row = self._itemList.rowCount()
        self._addItem(row)
        self._emitValueChanged()

    def onRemoveButtonClick(self):
        '''Handle remove button click.'''
        selectionModel = self._itemList.selectionModel()
        indexes = selectionModel.selectedRows()

        rows = []
        for index in indexes:
            rows.append(index.row())

        # Remove rows in reverse order to avoid incorrect index.
        rows = sorted(rows, reverse=True)
        for row in rows:
            self._itemList.removeRow(row)

        self._emitValueChanged()

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(Array, self).setTitle(value)

        title = self._title
        if self.required():
            title += '*'

        self._titleLabel.setText(title)

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        super(Array, self).setRequired(value)
        self.setTitle(self.title())

    def setError(self, value):
        '''Set error to *value*.

        *value* can be either a dictionary or a string.

        If *value* is a dictionary then each entry should correspond to a
        the index of a current item.

        If *value* is a string it will be displayed at the container level.

        '''
        self._error = value

        if isinstance(value, basestring):
            if value:
                self._errorIndicator.setPixmap(QtGui.QPixmap(':icon_error'))
                self._errorIndicator.setToolTip(value)
            else:
                self._errorIndicator.setPixmap(QtGui.QPixmap(':icon_blank'))
                self._errorIndicator.setToolTip('')

        else:
            self._errorIndicator.setPixmap(QtGui.QPixmap(':icon_blank'))
            self._errorIndicator.setToolTip('')
            if value is None:
                value = {}

            for row, error in value.items():
                widget = self._itemList.cellWidget(row, 0)
                widget.setError(error)

    def value(self):
        '''Return current value.

        Combine all child values into a list.

        '''
        value = []

        for row in range(self._itemList.rowCount()):
            widget = self._itemList.cellWidget(row, 0)
            value.append(widget.value())

        return value

    def setValue(self, value):
        '''Set current *value*.

        *value* should be a list of values to be displayed in this
        widgets item list.

        .. note::

            Will first remove all existing rows.

        '''
        self._itemList.clear()
        self._itemList.setRowCount(0)

        if value is None:
            value = []

        for row, item_value in enumerate(value):
            self._addItem(row, item_value)

        self._emitValueChanged()

    def _addItem(self, row, value=None):
        '''Add an appropriate item at *row* with *value*.'''
        try:
            item = self._types[row]
        except IndexError:
            item = self._additionalType

        widget = item['constructor']()

        if value is not None:
            widget.setValue(value)

        elif 'value' in item:
            widget.setValue(item['value'])

        widget.valueChanged.connect(self._emitValueChanged)

        self._itemList.insertRow(row)
        self._itemList.setCellWidget(row, 0, widget)

        self._itemList.resizeRowToContents(row)
