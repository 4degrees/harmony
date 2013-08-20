# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .base import Widget


class Simple(Widget):
    '''Simple widget that wraps a single control.'''

    def _construct(self, **kw):
        '''Construct widget.'''
        super(Simple, self)._construct(**kw)
        self.setLayout(QtGui.QHBoxLayout())

        self.layout().addWidget(self._requiredIndicator)
        self.layout().addWidget(self._titleLabel)

        self._prefix = QtGui.QFrame()
        self._prefix.setLayout(QtGui.QHBoxLayout())
        self._prefix.layout().addWidget(self._requiredIndicator)
        self._prefix.layout().addWidget(self._titleLabel)
        self.layout().addWidget(self._prefix, stretch=0)

        self._control = self._constructControl(**kw)
        self.layout().addWidget(self._control, stretch=1)
        self.layout().addWidget(self._errorIndicator, stretch=0)

    def _constructControl(self, **kw):
        '''Return the control widget.

        Subclasses should override this to return an appropriate control
        widget.

        '''
        raise NotImplementedError()

    def value(self):
        '''Return current value.'''
        raise NotImplementedError()

    def setValue(self, value):
        '''Set current *value*.'''
        raise NotImplementedError()
