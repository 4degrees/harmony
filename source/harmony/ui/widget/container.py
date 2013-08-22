# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .base import Widget


class Container(Widget):
    '''Group together several related widgets.'''

    def __init__(self, children, columns=1, **kw):
        '''Initialise widget with *children*.

        *children* should be list of dictionaries. Each dictionary should
        have the following keys:

            * name - Required name to key the widget under. Used in he return
              value to scope the value of the child.
            * widget - Required widget instance to represent child.

        '''
        self.children = children
        self._columns = columns
        super(Container, self).__init__(**kw)

    def _construct(self):
        '''Construct the interface.'''
        super(Container, self)._construct()
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        self.setLineWidth(1)

        self.setLayout(QtGui.QVBoxLayout())

        self._header = QtGui.QFrame()
        self._header.setLayout(QtGui.QHBoxLayout())

        self._titleLabel = QtGui.QLabel()

        self._header.layout().addWidget(self._titleLabel, stretch=0)
        self._header.layout().addStretch(1)
        self._header.layout().addWidget(self._errorIndicator, stretch=0)
        self._header.layout().setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(self._header, stretch=0)

        # Layout children
        self._childrenLayout = QtGui.QGridLayout()

        row = 0
        for index, child in enumerate(self.children):
            column = index % self._columns
            self._childrenLayout.addWidget(child['widget'], row, column)

            if column == self._columns - 1:
                row += 1

        self.layout().addLayout(self._childrenLayout, stretch=1)

        self.setSizePolicy(
               QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )

        self.layout().setContentsMargins(5, 5, 5, 5)

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        # Relay child value changed signal.
        for child in self.children:
            child['widget'].valueChanged.connect(self._emitValueChanged)

        super(Container, self)._postConstruction()

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(Container, self).setTitle(value)

        placeholder = self._title
        if not self.required():
            placeholder += ' (optional)'

        self._titleLabel.setText(placeholder)

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        super(Container, self).setRequired(value)
        self.setTitle(self.title())

    def setError(self, value):
        '''Set error to *value*.

        *value* can be either a dictionary or a string.

        If *value* is a dictionary then each key should correspond to the name
        of a child of this container and that key's value the error to set for
        the child.

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

            for child in self.children:
                child_error = value.get(child['name'], None)
                child['widget'].setError(child_error)

    def value(self):
        '''Return current value.

        Combine all child values into a dictionary keyed by the child name as
        passed in self.children.

        Do not include child values that are None to help ensure validation
        errors are not misleading.

        '''
        value = {}

        for child in self.children:
            child_value = child['widget'].value()

            # Ignore None values
            if child_value is None:
                continue

            value[child['name']] = child_value

        return value

    def setValue(self, value):
        '''Set current *value*.

        *value* must be a dictionary with each key corresponding to the name
        of a child of this container and that key's value the value to set for
        the child.

        '''
        children_by_name = {}
        for child in self.children:
            children_by_name[child['name']] = child['widget']

        for child_name, child_value in value.items():
            child = children_by_name.get(child_name)
            if child:
                child.setValue(child_value)

