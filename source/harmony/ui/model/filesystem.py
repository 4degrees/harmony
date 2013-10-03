# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
from datetime import datetime

from PySide.QtCore import Qt, QAbstractItemModel, QModelIndex, QDir, QFileInfo
from PySide.QtGui import QIcon, QFileIconProvider, QSortFilterProxyModel
import clique


class FilesystemItem(object):
    '''Represent filesystem item.'''

    def __init__(self, path, parent=None):
        '''Initialise item with *path*.

        *parent* is the parent :py:class:`FilesystemItem` if this item is a
        child.

        '''
        super(FilesystemItem, self).__init__()
        self.path = path
        self.parent = parent
        if parent is not None:
            parent.addChild(self)

        self.children = []
        self._fetched = False

    def __repr__(self):
        '''Return representation.'''
        return '<{0} {1}>'.format(self.__class__.__name__, self.path)

    @property
    def name(self):
        '''Return name of item.'''
        return os.path.basename(self.path) or self.path

    @property
    def size(self):
        '''Return size of item.'''
        return os.path.getsize(self.path)

    @property
    def type(self):
        '''Return type of item as string.'''
        return ''

    @property
    def modified(self):
        '''Return last modified date of item.'''
        return datetime.fromtimestamp(os.path.getmtime(self.path))

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

    def canFetchMore(self):
        '''Return whether more items can be fetched under this one.'''
        if not self._fetched:
            if self.mayHaveChildren():
                return True

        return False

    def mayHaveChildren(self):
        '''Return whether item may have children.'''
        return True

    def fetchChildren(self):
        '''Load children.

        Will only fetch children whilst canFetchMore is True. Each child
        will be added as a new :py:class:`FilesystemItem` to the children list
        of this item and their parent will be set to this item.

        '''
        if not self.canFetchMore():
            return

        children = self._fetchChildren()
        for child in children:
            self.addChild(child)

        self._fetched = True

    def _fetchChildren(self):
        '''Fetch child items.

        Override in subclasses to fetch actual children and return list of
        unparented :py:class:`FilesystemItem` instances.

        '''
        return []

    def refetch(self):
        '''Reload children.'''
        # Reset children
        for child in self.children[:]:
            self.removeChild(child)

        # Enable children fetching
        self._fetched = False


class FilesystemRoot(FilesystemItem):
    '''Represent root.'''

    def __init__(self, parent=None):
        '''Initialise item.

        *parent* is the parent :py:class:`FilesystemItem` if this item is a
        child.

        '''
        super(FilesystemRoot, self).__init__('', parent=parent)

    @property
    def name(self):
        '''Return name of item.'''
        return 'Computer'

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Root'

    def _fetchChildren(self):
        '''Fetch child items.'''
        children = []
        for entry in QDir.drives():
            path = os.path.normpath(entry.canonicalPath())
            children.append(FilesystemMount(path))

        return children


class FilesystemFile(FilesystemItem):
    '''Represent file.'''

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'File'

    def mayHaveChildren(self):
        '''Return whether item may have children.'''
        return False


class FilesystemDirectory(FilesystemItem):
    '''Represent directory.'''

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Directory'

    def _fetchChildren(self):
        '''Fetch child items.'''
        children = []

        # List paths under this directory.
        paths = []
        for name in os.listdir(self.path):
            paths.append(os.path.normpath(os.path.join(self.path, name)))

        # Handle collections.
        # TODO: When https://github.com/4degrees/clique/issues/4 resolved
        # can update this to avoid extra processing.
        collections = clique.assemble(paths, [clique.PATTERNS['frames']])

        for path in paths:
            collected = False

            for collection in collections:
                if path in collection:
                    collected = True
                    break

            if not collected:
                child = None

                if os.path.isfile(path):
                    child = FilesystemFile(path)

                elif os.path.ismount(path):
                    child = FilesystemMount(path)

                elif os.path.isdir(path):
                    child = FilesystemDirectory(path)

                if child is not None:
                    children.append(child)

        for collection in collections:
            children.append(FilesystemCollection(collection))

        return children


class FilesystemMount(FilesystemDirectory):
    '''Represent mount point.'''

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Mount'

    @property
    def size(self):
        '''Return size of item.'''
        return None

    @property
    def modified(self):
        '''Return last modified date of item.'''
        return None


class FilesystemCollection(FilesystemItem):
    '''Represent collection.'''

    def __init__(self, collection, parent=None):
        '''Initialise item with *collection*.

        *collection* should be an instance of :py:class:`clique.Collection`.

        *parent* is the parent :py:class:`FilesystemItem` if this item is a
        child.

        '''
        self._collection = collection
        super(FilesystemCollection, self).__init__(self._collection.format(),
                                                   parent=parent)

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Collection'

    @property
    def size(self):
        '''Return size of item.'''
        return None

    @property
    def modified(self):
        '''Return last modified date of item.'''
        return None

    def _fetchChildren(self):
        '''Fetch child items.'''
        children = []
        for path in self._collection:
            child = None

            if os.path.isfile(path):
                    child = FilesystemFile(path)

            elif os.path.ismount(path):
                child = FilesystemMount(path)

            elif os.path.isdir(path):
                child = FilesystemDirectory(path)

            if child is not None:
                children.append(child)

        return children


class Filesystem(QAbstractItemModel):
    '''Model representing filesystem.'''

    ITEM_ROLE = Qt.UserRole + 1

    def __init__(self, path='', parent=None):
        '''Initialise with root *path*.'''
        super(Filesystem, self).__init__(parent=parent)
        self.path = path
        self.columns = ['Name', 'Size', 'Type', 'Date Modified']
        self.iconFactory = QFileIconProvider()
        self.root = FilesystemRoot()

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
            elif column == 1:
                if item.size:
                    return item.size
            elif column == 2:
                return item.type
            elif column == 3:
                if item.modified is not None:
                    return item.modified.strftime('%c')

        elif role == Qt.DecorationRole:
            if column == 0:
                icon = self.iconFactory.icon(QFileInfo(item.path))

                if icon is None or icon.isNull():
                    if isinstance(item, FilesystemDirectory):
                        icon = QIcon(':icon_folder')
                    elif isinstance(item, FilesystemMount):
                        icon = QIcon(':icon_drive')
                    elif isinstance(item, FilesystemCollection):
                        icon = QIcon(':icon_collection')
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

        return item.mayHaveChildren()

    def canFetchMore(self, index):
        '''Return if more data available for *index*.'''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()

        return item.canFetchMore()

    def fetchMore(self, index):
        '''Fetch additional data under *index*.'''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()

        if item.canFetchMore():
            current_index = len(item.children)
            item.fetchChildren()
            new_index = len(item.children) - 1
            if new_index >= current_index:
                self.beginInsertRows(index, current_index, new_index)
                self.endInsertRows()

    def reset(self):
        '''Reset model'''
        self.beginResetModel()
        self.root = FilesystemRoot()
        self.root.refetch()
        self.endResetModel()


class FilesystemSortProxy(QSortFilterProxyModel):
    '''Sort directories before files.'''

    def lessThan(self, left, right):
        '''Return ordering of *left* vs *right*.'''
        sourceModel = self.sourceModel()
        if sourceModel:
            leftItem = sourceModel.item(left)
            rightItem = sourceModel.item(right)

            if (isinstance(leftItem, FilesystemDirectory)
                and not isinstance(rightItem, FilesystemDirectory)):
                return self.sortOrder() == Qt.AscendingOrder

            elif (not isinstance(leftItem, FilesystemDirectory)
                and isinstance(rightItem, FilesystemDirectory)):
                return self.sortOrder() == Qt.DescendingOrder

        return super(FilesystemSortProxy, self).lessThan(left, right)

    @property
    def root(self):
        '''Return root of model.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return None

        return sourceModel.root

    @property
    def iconFactory(self):
        '''Return iconFactory of model.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return None

        return sourceModel.iconFactory

    def pathIndex(self, path):
        '''Return index of item with *path*.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return QModelIndex()

        return self.mapFromSource(sourceModel.pathIndex(path))

    def item(self, index):
        '''Return item at *index*.'''
        sourceModel = self.sourceModel()

        if not sourceModel:
            return None

        return sourceModel.item(self.mapToSource(index))

    def icon(self, index):
        '''Return icon for index.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return None

        return sourceModel.icon(self.mapToSource(index))
