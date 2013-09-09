# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import copy

from PySide import QtGui, QtCore

import harmony.ui.error_tree
import harmony.ui.worker


class Publisher(QtGui.QDialog):
    '''Publisher dialog.'''

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

        self._schemaDetailsArea.setFrameStyle(
            QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain
        )

        self._schemaDetailsArea.setWidget(schemaDetails)

        # Connect dynamic validation.
        schemaDetails.valueChanged.connect(self._onValueChanged)

        # Construct initial data and set.
        instance = self._session.instantiate(schema)
        schemaDetails.setValue(instance)

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
                '\n{0}'.format(error)
            )

        else:
            process_dialog.reset()
            QtGui.QMessageBox.information(
                self,
                'Publish completed',
                'Publish completed successfully!'
                '\n{0}'.format(worker.result or '')
            )

        self._postPublish()

    def _publish(self, instance):
        '''Publish *instance*.

        Override in subclasses to perform actual publish.

        '''

    def _postPublish(self):
        '''Perform post publish action.'''
        self._prepareSubsequentPublish()

    def _prepareSubsequentPublish(self):
        '''Clean instance data in preparation for subsequent publish.'''
        instance = self._schemaDetailsArea.widget().value()
        newInstance = copy.deepcopy(instance)
        for key in ('id', 'created', 'modified'):
            newInstance.pop(key, None)

        self._schemaDetailsArea.widget().setValue(newInstance)
