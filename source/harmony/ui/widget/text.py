# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui, QtCore

from .string import String


class Text(String):
    '''Multiple line text based input.'''

    def _constructControl(self):
        '''Return the control widget.'''
        control = TextEdit()

        # Default to 5 lines high.
        # TODO: Make this configurable?
        font_metrics = QtGui.QFontMetrics(control.font())
        control.setFixedHeight((font_metrics.lineSpacing() * 5) + 10)

        return control


class TextEdit(QtGui.QPlainTextEdit):
    '''Text edit with support for placeholder text.'''

    def __init__(self, *args, **kw):
        '''Initialise text edit.'''
        self._placeholderText = ''
        super(TextEdit, self).__init__(*args, **kw)
        self.setTabChangesFocus(True)

    def placeholderText(self):
        '''Return placeholder text.'''
        return self._placeholderText

    def setPlaceholderText(self, value):
        '''Set placeholder text to *value*.'''
        self._placeholderText = value

    def text(self):
        '''Return current text.'''
        return self.toPlainText()

    def setText(self, value):
        '''Set text to *value*.'''
        self.setPlainText(value)

    def focusInEvent(self, event):
        '''Handle focus in event.'''
        super(TextEdit, self).focusInEvent(event)
        self.viewport().update()

    def focusOutEvent(self, event):
        '''Handle focus out event.'''
        super(TextEdit, self).focusOutEvent(event)
        self.viewport().update()

    def paintEvent(self, event):
        '''Handle paint *event*.'''
        placeholder = self.placeholderText()
        if placeholder and not self.toPlainText() and not self.hasFocus():
            # Display a placeholder
            viewport = self.viewport()
            target = viewport.rect()
            palette = self.palette()

            painter = QtGui.QPainter(viewport)

            previous_pen = painter.pen()
            color = palette.text().color()
            color.setAlpha(128)  # 50% of text color
            painter.setPen(color)

            painter.drawText(
                target.adjusted(4, 4, -4, -4),  # TODO: How to calculate?
                QtCore.Qt.AlignLeft,
                placeholder
            )

            painter.setPen(previous_pen)
            painter.end()

        super(TextEdit, self).paintEvent(event)

