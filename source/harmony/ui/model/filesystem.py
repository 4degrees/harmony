# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os

from PySide.QtCore import Qt, QAbstractItemModel, QModelIndex, QDir, QFileInfo
from PySide.QtGui import QIcon, QFileIconProvider


class FilesystemItem(object):
    '''Represent filesystem item.'''

    def __init__(self, info, parent=None):
        '''Initialise item with *info*.

        *info* should be an instance of :py:class:`PySide.QtCore.QFileInfo`.

        *parent* is the parent :py:class:`FilesystemItem` if this item is a
        child.

        '''
        super(FilesystemItem, self).__init__()
        self.info = info
        self.parent = parent
        if parent is not None:
            parent.addChild(self)

        self.children = []
        self.canFetchMore = not self.isFile()

    def __repr__(self):
        '''Return representation.'''
        return '<{0} {1}>'.format(self.__class__.__name__, self.path)

    @property
    def path(self):
        '''Return absolute path.'''
        return self.info.absoluteFilePath()

    @property
    def name(self):
        '''Return name of item.'''
        return self.info.fileName() or self.info.canonicalPath() or 'Computer'

    @property
    def row(self):
        '''Return index of this item in its parent or 0 if no parent.'''
        if self.parent:
            return self.parent.children.index(self)

        return 0

    def addChild(self, item):
        '''Add *item* as child of this item.'''
        if item.parent and item.parent != self:
            item.parent.removeChild(item)

        self.children.append(item)
        item.parent = self

    def removeChild(self, item):
        '''Remove *item* from children.'''
        item.parent = None
        self.children.remove(item)

    def fetchChildren(self):
        '''Load children.

        Will only fetch children whilst canFetchMore is True. Each child
        will be added as a new :py:class:`FilesystemItem` to the children list
        of this item and their parent will be set to this item.

        '''
        if not self.canFetchMore:
            return

        if self.path == '':
            # Handle root drive.
            entries = QDir.drives()
        else:
            directory = QDir(self.path)
            entries = directory.entryInfoList(
                QDir.AllEntries | QDir.NoDotAndDotDot
            )

        for entry in entries:
            FilesystemItem(entry, parent=self)

        self.canFetchMore = False

    def refetch(self):
        '''Reload children.'''
        # Reset children
        for child in self.children[:]:
            self.removeChild(child)

        # Enable children fetching
        self.canFetchMore = not self.isFile()

    def isFile(self):
        '''Return whether item represents a file.'''
        return os.path.isfile(self.path)

    def isDirectory(self):
        '''Return whether item represents a directory.'''
        return os.path.isdir(self.path)

    def isMount(self):
        '''Return whether item represents a mount point.'''
        return os.path.ismount(self.path)


class Filesystem(QAbstractItemModel):
    '''Model representing filesystem.'''

    ITEM_ROLE = Qt.UserRole + 1

    def __init__(self, path='', parent=None):
        '''Initialise with root *path*.'''
        super(Filesystem, self).__init__(parent=parent)
        self.path = path
        self.columns = ['Name', 'Size', 'Type', 'Date Modified']
        self.iconFactory = QFileIconProvider()
        self.root = FilesystemItem(QFileInfo())
        
    def rowCount(self, parent):
        '''Return number of children *parent* index has.'''
        if parent.column() > 0:
            return 0

        if parent.isValid():
            item = parent.internalPointer()
        else:
            item = self.root

        return len(item.children)

    def columnCount(self, parent):
        '''Return amount of data *parent* index has.'''
        return len(self.columns)

    def flags(self, index):
        '''Return flags for *index*.'''
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def index(self, row, column, parent):
        '''Return index for *row* and *column* under *parent*.'''
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            item = self.root
        else:
            item = parent.internalPointer()

        child = item.children[row]
        if child:
            return self.createIndex(row, column, child)
        else:
            return QModelIndex()

    def pathIndex(self, path):
        '''Return index of item with *path*.'''
        parts = []
        while True:
            head, tail = os.path.split(path)
            if head == path:
                if path:
                    parts.append(path)
                break

            parts.append(tail)
            path = head

        parts.reverse()
        if parts:
            item = self.root
            count = 0

            for count, part in enumerate(parts):
                matched = False
                for child in item.children:
                    if child.name == part:
                        item = child
                        matched = True
                        break
                if not matched:
                    break

            if count + 1 == len(parts):
                return self.createIndex(item.row, 0, item)

        return QModelIndex()

    def parent(self, index):
        '''Return parent of *index*.'''
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        parent = item.parent

        if parent == self.root:
            return QModelIndex()

        return self.createIndex(parent.row, 0, parent)

    def item(self, index):
        '''Return item at *index*.'''
        return self.data(index, role=self.ITEM_ROLE)

    def icon(self, index):
        '''Return icon for index.'''
        return self.data(index, role=Qt.DecorationRole)

    def data(self, index, role):
        '''Return data for *index* according to *role*.'''
        if not index.isValid():
            return None

        column = index.column()
        item = index.internalPointer()

        if role == self.ITEM_ROLE:
            return item

        elif role == Qt.DisplayRole:

            if column == 0:
                return item.name

        elif role == Qt.DecorationRole:
            if column == 0:
                icon = self.iconFactory.icon(item.info)

                if icon is None:
                    if item.isDirectory():
                        icon = QIcon(':icon_folder')
                    elif item.isMount():
                        icon = QIcon(':icon_drive')
                    else:
                        icon = QIcon(':icon_file')

                return icon

        elif role == Qt.TextAlignmentRole:
            if column == 1:
                return Qt.AlignRight
            else:
                return Qt.AlignLeft

        return None

    def headerData(self, section, orientation, role):
        '''Return label for *section* according to *orientation* and *role*.'''
        if orientation == Qt.Horizontal:
            if section < len(self.columns):
                column = self.columns[section]
                if role == Qt.DisplayRole:
                    return column

        return None

    def hasChildren(self, index):
        '''Return if *index* has children.

        Optimised to avoid loading children at this stage.

        '''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()
            if not item:
                return False

        return True

    def canFetchMore(self, index):
        '''Return if more data available for *index*.'''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()

        return item.canFetchMore

    def fetchMore(self, index):
        '''Fetch additional data under *index*.'''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()

        if item.canFetchMore:
            current_index = len(item.children)
            item.fetchChildren()
            new_index = len(item.children) - 1
            if new_index >= current_index:
                self.beginInsertRows(index, current_index, new_index)
                self.endInsertRows()

    def reset(self):
        '''Reset model'''
        self.beginResetModel()
        self.root = FilesystemItem(QFileInfo())
        self.root.refetch()
        self.endResetModel()
