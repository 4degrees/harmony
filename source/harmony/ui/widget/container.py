# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .base import Widget


class Container(Widget):
    '''Group together several related widgets.'''

    def __init__(self, children, **kw):
        '''Initialise widget with *children*.

        *children* should be list of dictionaries. Each dictionary should
        have the following keys:

            * name - Required name to key the widget under. Used in he return
              value to scope the value of the child.
            * widget - Required widget instance to represent child.

        '''
        self.children = children
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

        self._childrenLayout = QtGui.QVBoxLayout()

        for child in self.children:
            if child['widget']:
                self._childrenLayout.addWidget(child['widget'])

        self.layout().addLayout(self._childrenLayout, stretch=1)

        self.setSizePolicy(
               QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )

        self.layout().setContentsMargins(5, 5, 5, 5)

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
