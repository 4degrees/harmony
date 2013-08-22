# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore

from .simple import Simple


class DateTime(Simple):
    '''Date and time input.'''

    def _constructControl(self):
        '''Return the control widget.'''
        control = DateTimeEdit()
        control.setCalendarPopup(True)
        control.setSpecialValueText('NOW')
        return control

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        super(DateTime, self)._postConstruction()
        self._control.dateTimeChanged.connect(self._emitValueChanged)

    def setTitle(self, value):
        '''Set title to *value*.'''
        super(DateTime, self).setTitle(value)

        placeholder = self._title
        if not self.required():
            placeholder += ' (optional)'

        self._control.setPlaceholderText(placeholder)

    def setRequired(self, value):
        '''Set required status to boolean *value*.'''
        super(DateTime, self).setRequired(value)
        self.setTitle(self.title())

    def value(self):
        '''Return current value.'''
        value = self._control.dateTime()
        if value is None:
            return value

        return value.toString(QtCore.Qt.ISODate)

    def setValue(self, value):
        '''Set current *value*.'''
        if value is not None:
            value = QtCore.QDateTime.fromString(value, QtCore.Qt.ISODate)

        self._control.setDateTime(value)


class DateTimeEdit(QtGui.QDateTimeEdit):
    '''Date time edit with support for placeholder text and nullable value.'''

    def __init__(self, *args, **kw):
        '''Initialise date time edit.'''
        self._placeholderText = ''
        self._isNull = False
        super(DateTimeEdit, self).__init__(*args, **kw)
        self.setDateTime(None)

    def setDateTime(self, value):
        '''Set date time to *value*.'''
        if value is None:
            self._isNull = True
            self.dateTimeChanged.emit(value)
        else:
            self._isNull = False
            super(DateTimeEdit, self).setDateTime(value)

    def dateTime(self):
        '''Return date time.'''
        if self._isNull:
            return None
        else:
            return super(DateTimeEdit, self).dateTime()

    def setDate(self, value):
        '''Set date to *value*.'''
        if value is None:
            self._isNull = True
            self.dateChanged.emit(value)
        else:
            self._isNull = False
            super(DateTimeEdit, self).setDate(value)

    def date(self):
        '''Return date.'''
        if self._isNull:
            return None
        else:
            return super(DateTimeEdit, self).date()

    def setTime(self, value):
        '''Set time to *value*.'''
        if value is None:
            self._isNull = True
            self.timeChanged.emit(value)
        else:
            self._isNull = False
            super(DateTimeEdit, self).setTime(value)

    def time(self):
        '''Return time.'''
        if self._isNull:
            return None
        else:
            return super(DateTimeEdit, self).time()

    def placeholderText(self):
        '''Return placeholder text.'''
        return self._placeholderText

    def setPlaceholderText(self, value):
        '''Set placeholder text to *value*.'''
        self._placeholderText = value
        lineEdit = self.findChild(QtGui.QLineEdit)
        lineEdit.setPlaceholderText(value)

    def keyPressEvent(self, event):
        '''Handle key press *event*.'''
        key = event.key()

        if self._isNull:
            if key == QtCore.Qt.Key_Tab:
                QtGui.QAbstractSpinBox.keyPressEvent(self, event)
                return

            elif QtCore.Qt.Key_0 <= key <= QtCore.Qt.Key_9:
                self.setDateTime(QtCore.QDateTime.currentDateTime())
                return

        if key in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete):
            lineEdit = self.findChild(QtGui.QLineEdit)
            if lineEdit.selectedText() == lineEdit.text():
                event.accept()
                self.setDateTime(None)

                return

        super(DateTimeEdit, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        '''Handle mouse press *event*.'''
        super(DateTimeEdit, self).mousePressEvent(event)
        if self._isNull and self.calendarWidget().isVisible():
            self.setDateTime(QtCore.QDateTime.currentDateTime())

    def focusNextPrevChild(self, value):
        '''Focus next/previous child according to *value*.'''
        if self._isNull:
            return QtGui.QAbstractSpinBox.focusNextPrevChild(self, value)
        else:
            return super(DateTimeEdit, self).focusNextPrevChild(value)

    def paintEvent(self, event):
        '''Handle paint *event*.'''
        if self._isNull:
            # Display a placeholder
            lineEdit = self.findChild(QtGui.QLineEdit)
            lineEdit.setText('')

        super(DateTimeEdit, self).paintEvent(event)

