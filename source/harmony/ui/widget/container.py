# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import collections

from PySide import QtGui, QtCore

from .standard import Standard


class Container(Standard):
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
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        self.setLineWidth(1)

        font = QtGui.QFont(self._titleLabel.font())
        font.setBold(True)
        self._titleLabel.setFont(font)
        self._titleLabel.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )

        self._headerLayout.insertStretch(1, stretch=1)

        # Layout children
        self._childrenLayout = QtGui.QGridLayout()

        row = 0
        for index, child in enumerate(self.children):
            column = index % self._columns
            self._childrenLayout.addWidget(child['widget'], row, column)

            if column == self._columns - 1:
                row += 1

        self.layout().addLayout(self._childrenLayout, stretch=1)

        self.layout().setContentsMargins(5, 5, 5, 5)

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        # Relay child value changed signal.
        for child in self.children:
            child['widget'].valueChanged.connect(self._emitValueChanged)

        super(Container, self)._postConstruction()

    def setError(self, value):
        '''Set error to *value*.

        *value* can be either a dictionary or a string.

        If *value* is a dictionary then each key should correspond to the name
        of a child of this container and that key's value the error to set for
        the child. The special key '__self__' can be used to set an error
        at the container level as well as child levels.

        If *value* is a string it will be displayed at the container level.

        '''
        childValues = {}

        if isinstance(value, basestring):
            super(Container, self).setError(value)

        elif isinstance(value, collections.Mapping):
            childValues = value

            if '__self__' in value:
                super(Container, self).setError(value['__self__'])
            else:
                super(Container, self).setError(None)

        for child in self.children:
            child_error = childValues.get(child['name'], None)
            child['widget'].setError(child_error)

        # Set at end to override parent class.
        self._error = value

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
        the child. If a child is not included in *value* then it will have its
        value set to None.

        '''
        children_by_name = {}
        for child in self.children:
            children_by_name[child['name']] = child['widget']

        children_set = set([])
        for child_name, child_value in value.items():
            child = children_by_name.get(child_name)
            if child:
                child.setValue(child_value)
                children_set.add(child_name)

        for child_name, child in children_by_name.items():
            if child_name not in children_set:
                child.setValue(None)
