# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore

from .. import icon


class Widget(QtGui.QFrame):
    '''Base widget.

    Subclass to create widgets that reflect specific schema fragments.

    '''

    # Emit when value changes.
    valueChanged = QtCore.Signal()

    def __init__(self, title=None, description=None, required=False,
                 parent=None):
        '''Initialise widget with *parent*.'''
        super(Widget, self).__init__(parent=parent)
        self._title = title
        self._description = description
        self._required = required
        self._error = None

        self._construct()
        self._postConstruction()

    def _construct(self):
        '''Construct widget.'''
        self._errorIndicator = QtGui.QLabel()

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        self.setTitle(self._title)
        self.setDescription(self._description)
        self.setRequired(self._required)
        self.setError('')

    def _emitValueChanged(self, *args, **kw):
        '''Emit valueChanged signal.

        Subclasses should call this to notify system that the value has changed
        either programmatically or as a result of user input.

        '''
        self.valueChanged.emit()

    def title(self):
        '''Return title value as stored in widget.'''
        return self._title

    def setTitle(self, value):
        '''Set title to *value*.'''
        self._title = value

    def description(self):
        '''Return description value as stored in widget.'''
        return self._description

    def setDescription(self, value):
        '''Set description to *value*.'''
        self._description = value

    def required(self):
        '''Return current required status.'''
        return self._required

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        self._required = value

    def error(self):
        '''Return current error value.'''
        return self._error

    def setError(self, value):
        '''Set error to *value*.'''
        self._error = value
        if value:
            self._errorIndicator.setPixmap(QtGui.QPixmap(':icon_error'))
            self._errorIndicator.setToolTip(value)
        else:
            self._errorIndicator.setPixmap(QtGui.QPixmap(':icon_blank'))
            self._errorIndicator.setToolTip('')

    def value(self):
        '''Return current value.

        Return None if value should be considered as not set.

        '''
        raise NotImplementedError()

    def setValue(self, value):
        '''Set current *value*.'''
        raise NotImplementedError()
