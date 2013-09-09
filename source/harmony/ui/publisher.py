# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from PySide import QtGui

import harmony.ui.error_tree


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


