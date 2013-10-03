# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.
import os

from PySide import QtGui, QtCore

import harmony.ui.icon
import harmony.ui.model.filesystem


class FilesystemBrowser(QtGui.QDialog):
    '''FilesystemBrowser dialog.'''

    def __init__(self, parent=None):
        '''Initialise *parent*.

        *parent* is the optional owner of this UI element.

        '''
        super(FilesystemBrowser, self).__init__(parent=parent)
        self._selected = []
        self._construct()
        self._postConstruction()

    def _construct(self):
        '''Construct widget.'''
        self.setLayout(QtGui.QVBoxLayout())

        self._headerLayout = QtGui.QHBoxLayout()

        self._locationWidget = QtGui.QComboBox()
        self._headerLayout.addWidget(self._locationWidget, stretch=1)

        self._upButton = QtGui.QToolButton()
        self._upButton.setIcon(
            QtGui.QIcon.fromTheme('go-up', QtGui.QIcon(':icon_up'))
        )
        self._headerLayout.addWidget(self._upButton)

        self.layout().addLayout(self._headerLayout)

        self._contentSplitter = QtGui.QSplitter()

        self._bookmarksWidget = QtGui.QListView()
        self._contentSplitter.addWidget(self._bookmarksWidget)

        self._filesystemWidget = QtGui.QTableView()
        self._filesystemWidget.setSelectionBehavior(
            self._filesystemWidget.SelectRows
        )
        self._filesystemWidget.setSelectionMode(
            self._filesystemWidget.SingleSelection
        )
        self._filesystemWidget.verticalHeader().hide()

        self._contentSplitter.addWidget(self._filesystemWidget)

        proxy = harmony.ui.model.filesystem.FilesystemSortProxy(self)
        model = harmony.ui.model.filesystem.Filesystem(self)
        proxy.setSourceModel(model)
        self._filesystemWidget.setModel(proxy)
        self._filesystemWidget.setSortingEnabled(True)

        self._contentSplitter.setStretchFactor(1, 1)
        self.layout().addWidget(self._contentSplitter)

        self._footerLayout = QtGui.QHBoxLayout()
        self._footerLayout.addStretch(1)

        self._cancelButton = QtGui.QPushButton('Cancel')
        self._footerLayout.addWidget(self._cancelButton)

        self._acceptButton = QtGui.QPushButton('Choose')
        self._footerLayout.addWidget(self._acceptButton)

        self.layout().addLayout(self._footerLayout)

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        self.setWindowTitle('Filesystem Browser')
        self._filesystemWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # TODO: Remove once bookmarks widget implemented.
        self._bookmarksWidget.hide()

        self._acceptButton.setDefault(True)
        self._acceptButton.setDisabled(True)

        self._acceptButton.clicked.connect(self.accept)
        self._cancelButton.clicked.connect(self.reject)

        self.setLocation('')

        self._filesystemWidget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents
        )
        self._filesystemWidget.horizontalHeader().setResizeMode(
            0, QtGui.QHeaderView.Stretch
        )

        self._upButton.clicked.connect(self._onNavigateUpButtonClicked)
        self._locationWidget.currentIndexChanged.connect(
            self._onNavigate
        )

        self._filesystemWidget.activated.connect(self._onActivateItem)
        selectionModel = self._filesystemWidget.selectionModel()
        selectionModel.currentRowChanged.connect(self._onSelectItem)

    def _onActivateItem(self, index):
        '''Handle activation of item in listing.'''
        item = self._filesystemWidget.model().item(index)
        if not isinstance(item, harmony.ui.model.filesystem.FilesystemFile):
            self._acceptButton.setDisabled(True)
            self.setLocation(item.path)

    def _onSelectItem(self, selection, previousSelection):
        '''Handle selection of item in listing.'''
        self._acceptButton.setEnabled(True)
        del self._selected[:]
        item = self._filesystemWidget.model().item(selection)
        self._selected.append(item.path)

    def _onNavigate(self, index):
        '''Handle selection of path segment.'''
        if index > 0:
            self.setLocation(self._locationWidget.itemData(index))

    def _onNavigateUpButtonClicked(self):
        '''Navigate up a directory on button click.'''
        index = self._locationWidget.currentIndex()
        self._onNavigate(index + 1)

    def _segmentPath(self, path):
        '''Return list of valid *path* segments.'''
        parts = []
        while True:
            head, tail = os.path.split(path)
            if path:
                parts.append(path)

            if head == path:
                break

            path = head

        return parts

    def setLocation(self, path):
        '''Set current location to *path*.'''
        model = self._filesystemWidget.model()
        self._filesystemWidget.setRootIndex(model.pathIndex(path))

        self._locationWidget.clear()

        if path != model.root.path:
            segments = self._segmentPath(path)
            for segment in segments:
                icon = model.icon(model.pathIndex(segment))
                self._locationWidget.addItem(icon, segment, segment)

        rootIcon = model.iconFactory.icon(model.iconFactory.Computer)
        if rootIcon is None:
            rootIcon = QtGui.QIcon(':icon_folder')

        self._locationWidget.addItem(rootIcon, model.root.name, model.root.path)

        if self._locationWidget.count() > 1:
            self._upButton.setEnabled(True)
        else:
            self._upButton.setEnabled(False)

    def selected(self):
        '''Return selected paths.'''
        return self._selected[:]
