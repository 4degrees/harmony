# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore


class Widget(QtGui.QFrame):
    '''Base widget.

    Subclass to create widgets that reflect specific schema fragments.

    '''

    # Emit when value changes.
    value_changed = QtCore.Signal()

    def __init__(self, title, description=None, required=False, value=None,
                 parent=None):
        '''Initialise widget with *parent*.'''
        super(Widget, self).__init__(parent=parent)

        self.construct()
        self.post_construction()

        self.title = title
        self.description = description
        self.required = required
        self.value = value

    @property
    def title(self):
        '''Return title value as stored in widget.'''
        return self.title_label.text()

    @title.setter
    def title(self, value):
        '''Set title to *value*.'''
        self.title_label.setText(value)

    @property
    def description(self):
        '''Return description value as stored in widget.'''
        return self.title_label.toolTip()

    @description.setter
    def description(self, value):
        '''Set description to *value*.'''
        self.title_label.setToolTip(value)

    @property
    def required(self):
        '''Return current required status.'''
        return self.required_indicator.pixmap() != None

    @required.setter
    def required(self, value):
        '''Set required status to boolean *value*.'''
        if value:
            self.required_indicator.setPixmap(QtGui.QPixmap())
            self.required_indicator.setToolTip('Required')
        else:
            self.required_indicator.setPixmap(QtGui.QPixmap())
            self.required_indicator.setToolTip('')

    @property
    def value(self):
        '''Return current value.'''
        raise NotImplementedError()

    @value.setter
    def value(self, value):
        '''Set current *value*.'''
        raise NotImplementedError()

    def construct(self):
        '''Construct widget.'''
        self.title_label = QtGui.QLabel()
        self.required_indicator = QtGui.QLabel()
        self.error_indicator = QtGui.QLabel()

    def post_construction(self):
        '''Perform post-construction operations.'''
