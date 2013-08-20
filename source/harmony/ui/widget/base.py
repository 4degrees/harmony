# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore


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

        self._construct()
        self._postConstruction()

        self.setTitle(title)
        self.setDescription(description)
        self.setRequired(required)

    def _construct(self):
        '''Construct widget.'''
        self._titleLabel = QtGui.QLabel()
        self._requiredIndicator = QtGui.QLabel()
        self._errorIndicator = QtGui.QLabel()

    def _postConstruction(self):
        '''Perform post-construction operations.'''

    def _emitValueChanged(self, *args, **kw):
        '''Emit valueChanged signal.

        Subclasses should call this to notify system that the value has changed
        either programmatically or as a result of user input.

        '''
        self.valueChanged.emit()

    def title(self):
        '''Return title value as stored in widget.'''
        return self._titleLabel.text()

    def setTitle(self, value):
        '''Set title to *value*.'''
        self._titleLabel.setText(value)

    def description(self):
        '''Return description value as stored in widget.'''
        return self._titleLabel.toolTip()

    def setDescription(self, value):
        '''Set description to *value*.'''
        self._titleLabel.setToolTip(value)

    def required(self):
        '''Return current required status.'''
        return self._requiredIndicator.pixmap() != None

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        if value:
            self._requiredIndicator.setPixmap(QtGui.QPixmap())
            self._requiredIndicator.setToolTip('Required')
        else:
            self._requiredIndicator.setPixmap(QtGui.QPixmap())
            self._requiredIndicator.setToolTip('')

    def error(self):
        '''Return current error value.'''
        return self._errorIndicator.toolTip()

    def setError(self, value):
        '''Set error to *value*.'''
        if value:
            self._errorIndicator.setPixmap(QtGui.QPixmap())
            self._errorIndicator.setToolTip(value)
        else:
            self._errorIndicator.setPixmap(QtGui.QPixmap())
            self._errorIndicator.setToolTip('')

    def value(self):
        '''Return current value.'''
        raise NotImplementedError()

    def setValue(self, value):
        '''Set current *value*.'''
        raise NotImplementedError()
