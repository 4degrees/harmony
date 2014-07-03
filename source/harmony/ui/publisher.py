# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import copy
import traceback
import pprint

from PySide import QtGui, QtCore

import harmony.ui.error_tree
import harmony.ui.worker
import harmony.error


class Publisher(QtGui.QDialog):
    '''Publisher dialog.'''

    valueChanged = QtCore.Signal()

    def __init__(self, session, factory, parent=None):
        '''Initialise with *session*, widget *factory* and *parent*.

        *session* should be a :py:class:`~harmony._session.Session` instance
        providing access to available schemas.

        *factory* should be a :py:class:`~harmony.ui.widget._factory.Factory`
        instance responsible for returning appropriate widgets for schema
        fragments.

        *parent* is the optional owner of this UI element.

        '''
        super(Publisher, self).__init__(parent=parent)

        self._session = session
        self._factory = factory

        self._construct()
        self._postConstruction()

    def _construct(self):
        '''Construct widget.'''
        self.setLayout(QtGui.QVBoxLayout())

        self._schemaSelector = QtGui.QComboBox()
        self._schemaDetailsArea = QtGui.QScrollArea()
        self._schemaDetailsArea.setWidgetResizable(True)
        self._publishButton = QtGui.QPushButton('Publish')
        self._publishButton.setDisabled(True)

        self.layout().addWidget(self._schemaSelector, stretch=0)
        self.layout().addWidget(self._schemaDetailsArea, stretch=1)
        self.layout().addWidget(self._publishButton, stretch=0)

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        self.setWindowTitle('Harmony Publisher')

        self._schemaSelector.currentIndexChanged.connect(self._onSelectSchema)
        self._publishButton.clicked.connect(self._onPublishButtonClicked)

        for schema in sorted(self._filterSchemas(self._session.schemas)):
            self._schemaSelector.addItem(
                schema.get('title', schema['id']),
                schema
            )

    def _filterSchemas(self, schemas):
        '''Return a list of *schemas* to display as options in the selector.'''
        filtered = []
        for schema in schemas:
            if schema.get('id', '').startswith('harmony:/item/'):
                filtered.append(schema)

        return filtered

    def _onSelectSchema(self, index):
        '''Handle schema selection.'''
        # Cleanup any existing schema widgets.
        existingSchemaDetails = self._schemaDetailsArea.takeWidget()
        if existingSchemaDetails is not None:
            existingSchemaDetails.setParent(None)
            existingSchemaDetails.deleteLater()

        # Construct new schema widgets.
        schema = self._schemaSelector.itemData(index)
        schemaDetails = self._factory(schema)
        schemaDetails.setRequired(True)
        schemaDetails.setContentsMargins(5, 5, 5, 5)
        schemaDetails.setFrameStyle(QtGui.QFrame.NoFrame)
        schemaDetails.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding
        )

        self._schemaDetailsArea.setFrameStyle(
            QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain
        )
        self._schemaDetailsArea.setWidget(schemaDetails)

        # Connect dynamic validation.
        schemaDetails.valueChanged.connect(self._onValueChanged)

        # Construct initial data and set.
        instance = self._session.instantiate(schema)
        schemaDetails.setValue(instance)

    def setValue(self, value):
        '''Set *value* of current publisher data.

        *value* should be appropriate for the top most widget in the publisher,
        as specified by the configured widget factory. Typically this will be
        a dictionary.

        .. note::

            The *value* must be comprehensive as it will override any currently
            set value entirely. To set just one part of a structured value,
            request the current value, modify it and then set.

        Raise :py:exc:`harmony.ui.PublisherError` if no schema widget found to
        set value on.

        '''
        widget = self._schemaDetailsArea.widget()
        if widget:
            widget.setValue(value)
        else:
            raise harmony.error.PublisherError(
                'Cannot set value when no schema widget defined.'
            )

    def value(self):
        '''Return current value of publisher data.

        Raise :py:exc:`harmony.ui.PublisherError` if no schema widget found to
        retrieve value from.

        '''
        widget = self._schemaDetailsArea.widget()
        if widget:
            return widget.value()
        else:
            raise harmony.error.PublisherError(
                'Cannot retrieve value when no schema widget defined.'
            )

    def _onValueChanged(self):
        '''Handle change in value.'''
        schema = self._schemaSelector.itemData(
            self._schemaSelector.currentIndex()
        )

        self._publishButton.setDisabled(True)

        if not schema:
            return

        instance = self._schemaDetailsArea.widget().value()
        self.validate(instance, schema)

        # Emit value changed for publisher.
        self.valueChanged.emit()

    def validate(self, instance, schema):
        '''Validate *instance* against *schema* and update UI state.'''
        # Validate
        errors = self._session.validate(instance)

        # Construct error tree that maps errors to UI structure.
        error_tree = harmony.ui.error_tree.ErrorTree(errors)

        # Apply errors to interface.
        self._schemaDetailsArea.widget().setError(error_tree)
        if error_tree:
            self._publishButton.setDisabled(True)
        else:
            self._publishButton.setEnabled(True)

    def _onPublishButtonClicked(self):
        '''Handle publish button event.'''
        self.publish()

    def publish(self):
        '''Publish instance.'''
        instance = self._schemaDetailsArea.widget().value()

        process_dialog = QtGui.QProgressDialog(
            'Publishing in progress.', '', 0, 0, parent=self
        )
        process_dialog.setWindowTitle('Publishing')
        process_dialog.setWindowModality(QtCore.Qt.WindowModal)
        process_dialog.setMinimumDuration(0)
        process_dialog.setCancelButton(None)
        process_dialog.show()

        try:
            worker = harmony.ui.worker.Worker(self._publish, [instance])
            worker.start()

            while worker.isRunning():
                app = QtGui.QApplication.instance()
                app.processEvents()

            if worker.error:
                raise worker.error[1], None, worker.error[2]

        except Exception as error:
            process_dialog.reset()
            QtGui.QMessageBox.critical(
                self,
                'Publish Error',
                'The following error occurred whilst publishing:' +
                '\n{0}'.format(error) +
                '\n\n{0}'.format(traceback.format_exc())
            )

        else:
            process_dialog.reset()

            self._postPublish(instance, worker.result)

    def _publish(self, instance):
        '''Publish *instance* and return published instance.

        Override in subclasses to perform actual publish.

        '''

    def _postPublish(self, instance, published):
        '''Perform post publish action.

        *instance* is the instance from the interface, whilst *published* is
        the result returned from the :py:meth:`_publish` method.

        '''
        self._showPostPublishMessage(published)

        newInstance = self._prepareSubsequentPublish(instance)
        self._schemaDetailsArea.widget().setValue(newInstance)

    def _showPostPublishMessage(self, published):
        '''Display a publish completed message.

        *published* is the returned result from the publish.

        '''
        if published:
            published = pprint.pformat(published)

        QtGui.QMessageBox.information(
            self,
            'Publish completed',
            'Publish completed successfully!'
            '\n\n{0}'.format(published or '')
        )

    def _prepareSubsequentPublish(self, instance):
        '''Return copy of *instance* ready for subsequent publish.

        For example, remove "id" and "created" values.

        '''
        newInstance = copy.deepcopy(instance)
        for key in ('id', 'created', 'modified'):
            newInstance.pop(key, None)

        return newInstance
