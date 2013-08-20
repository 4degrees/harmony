# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys

from PySide import QtGui, QtCore

import harmony.session
import harmony.ui.widget.factory


class Demo(QtGui.QDialog):
    '''Demo dialog.'''

    def __init__(self, session, parent=None):
        '''Initialise demo with *session* and *parent*.'''
        super(Demo, self).__init__(parent=parent)

        self.session = session
        self.widget_factory = harmony.ui.widget.factory.Factory()

        self.construct()
        self.post_construction()

    def construct(self):
        '''Construct widget.'''
        self.setLayout(QtGui.QVBoxLayout())

        self.schema_selector = QtGui.QComboBox()
        self.schema_details_area = QtGui.QScrollArea()
        self.schema_details_area.setWidgetResizable(True)

        self.layout().addWidget(self.schema_selector, stretch=0)
        self.layout().addWidget(self.schema_details_area, stretch=1)

    def post_construction(self):
        '''Perform post-construction operations.'''
        self.setWindowTitle('Harmony UI Builder')
        self.setMinimumSize(800, 600)

        self.schema_selector.currentIndexChanged.connect(self.on_select_schema)

        schema_ids = set()
        for schema in self.session.schemas:
            schema_ids.add(schema.get('id'))

        for schema_id in sorted(schema_ids):
            self.schema_selector.addItem(schema_id)

    def on_select_schema(self, index):
        '''Handle schema selection.'''
        existing_schema_details = self.schema_details_area.takeWidget()
        if existing_schema_details is not None:
            existing_schema_details.setParent(None)
            existing_schema_details.deleteLater()

        selected_schema_id = self.schema_selector.itemText(index)
        schema = self.session.schemas.get(selected_schema_id)

        schema_details = self.widget_factory(schema)
        self.schema_details_area.setWidget(schema_details)


def main(arguments=None):
    '''Interactive test of dynamic UI building from schema.'''
    if arguments is None:
        arguments = sys.argv

    application = QtGui.QApplication(arguments)

    session = harmony.session.Session()
    dialog = Demo(session)
    dialog.show()

    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main())

