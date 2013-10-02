# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

from .string import String


class FilesystemPath(String):
    '''Represent a filesystem path.'''

    def _construct(self):
        '''Construct widget.'''
        super(FilesystemPath, self)._construct()
        self._browseButton = QtGui.QPushButton('Browse')
        self._browseButton.setToolTip('Browse for path.')
        self._headerLayout.insertWidget(2, self._browseButton, stretch=0)

        self._dialog = QtGui.QFileDialog()
        self._dialog.setFileMode(QtGui.QFileDialog.ExistingFile)

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        super(FilesystemPath, self)._postConstruction()
        self._browseButton.clicked.connect(self.browse)

    def browse(self):
        '''Show browse dialog and populate value with result.'''
        if self._dialog.exec_():
            names = self._dialog.selectedFiles()
            if names:
                self.setValue(names[0])
