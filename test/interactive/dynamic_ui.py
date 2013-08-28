# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys
from functools import partial

from PySide import QtGui, QtCore
import jsonpointer

import harmony.session
import harmony.ui.widget.factory


class Demo(QtGui.QDialog):
    '''Demo dialog.'''

    def __init__(self, session, parent=None):
        '''Initialise demo with *session* and *parent*.'''
        super(Demo, self).__init__(parent=parent)

        self.session = session
        self.widget_factory = Factory(self.session)

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

        self.schema_selector.currentIndexChanged.connect(self.on_select_schema)

        # Filter schemas
        schemas = []
        for schema in self.session.schemas:
            if schema.get('id', '').startswith('harmony:/item/'):
                schemas.append(schema)

        for schema in sorted(schemas):
            self.schema_selector.addItem(
                schema.get('title', schema['id']),
                schema
            )

    def on_select_schema(self, index):
        '''Handle schema selection.'''
        # Cleanup any existing schema widgets.
        existing_schema_details = self.schema_details_area.takeWidget()
        if existing_schema_details is not None:
            existing_schema_details.setParent(None)
            existing_schema_details.deleteLater()

        # Construct new schema widgets.
        schema = self.schema_selector.itemData(index)
        schema_details = self.widget_factory(schema)
        schema_details.setRequired(True)
        schema_details.setContentsMargins(5, 5, 5, 5)
        schema_details.setFrameStyle(QtGui.QFrame.NoFrame)

        self.schema_details_area.setFrameStyle(
            QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain
        )

        self.schema_details_area.setWidget(schema_details)

        # Connect dynamic validation.
        schema_details.valueChanged.connect(self.on_value_changed)

        # Construct initial data and set.
        instance = self.session.instantiate(schema)
        schema_details.setValue(instance)

    def on_value_changed(self):
        '''Handle change in value.'''
        schema = self.schema_selector.itemData(
            self.schema_selector.currentIndex()
        )

        if not schema:
            return

        instance = self.schema_details_area.widget().value()
        self.validate(instance, schema)

    def validate(self, instance, schema):
        '''Validate *instance* against *schema* and update UI state.'''
        # Validate
        errors = self.session.validate(instance)

        # Construct error tree that maps errors to UI structure.
        error_tree = {}
        for error in errors:
            error_branch = error_tree

            path = list(error.path)
            path.insert(0, '__root__')

            if error.validator == 'required':
                # Required is set one level above so have to retrieve final
                # path segment.
                schema_path = '/' + '/'.join(map(str, error.schema_path))
                segment = jsonpointer.resolve_pointer(
                    error.schema, schema_path
                )
                path.append(segment)

            for segment in path[:-1]:
                error_branch = error_branch.setdefault(segment, {})

            error_branch[path[-1]] = error.message

        self.schema_details_area.widget().setError(
            error_tree.get('__root__', None)
        )


class Factory(harmony.ui.widget.factory.Factory):
    '''Customised widget factory.'''

    def __init__(self, *args, **kw):
        self.project_tree = {}

        for show_key in ('show_a', 'show_b'):
            show = self.project_tree.setdefault(show_key, {})
            scenes = show['scenes'] = {}
            assets = show['assets'] = {}

            for scene_key in ('sc001', 'sc002', 'sc003'):
                scene = scenes[scene_key] = {}
                shots = scene['shots'] = {}

                for shot_key in ('001', '002', '003', '004'):
                    shot = shots[shot_key] = {}
                    shot['assets'] = {}

            if show_key == 'show_a':
                for asset_key in ('astronaut', 'space_station'):
                    assets[asset_key] = {}

            elif show_key == 'show_b':
                for asset_key in ('dinosaur', 'amber', 'scientist'):
                    assets[asset_key] = {}

        super(Factory, self).__init__(*args, **kw)

    def _query_users(self):
        '''Return a list of valid users.'''
        users = [
            {'firstname': 'Martin', 'lastname': 'Pengelly-Phillips',
             'email': 'martin@4degrees.ltd.uk', 'username': 'martin'},
            {'firstname': 'Joe', 'lastname': 'Blogs',
             'email': 'joe@example.com', 'username': 'joe'}
        ]

        return map(partial(self.session.instantiate, 'harmony:/user'), users)

    def _query_scopes(self, scope, domain=None):
        '''Return list of entries for *scope* using *domain*.'''
        scopes = []
        if domain is None:
            domain = {}

        if scope == 'show':
            shows = sorted(self.project_tree.keys())
            for show in shows:
                scopes.append({
                    'name': show.replace('_', ' ').title(),
                    'id': show
                })

        elif scope == 'scene':
            show_id = domain.get('show', {}).get('id')
            show = self.project_tree.get(show_id, {})
            scenes = sorted(show.get('scenes', {}).keys())
            for scene in scenes:
                scopes.append({
                    'name': scene.replace('_', ' ').title(),
                    'id': scene
                })

        elif scope == 'shot':
            show_id = domain.get('show', {}).get('id')
            scene_id = domain.get('scene', {}).get('id')

            show = self.project_tree.get(show_id, {})
            scenes = show.get('scenes', {})
            scene = scenes.get(scene_id, {})
            shots = sorted(scene.get('shots', {}).keys())

            for shot in shots:
                scopes.append({
                    'name': shot.replace('_', ' ').title(),
                    'id': shot
                })

        elif scope == 'asset':
            show_id = domain.get('show', {}).get('id')
            scene_id = domain.get('scene', {}).get('id')
            shot_id = domain.get('shot', {}).get('id')

            show = self.project_tree.get(show_id, {})
            scenes = show.get('scenes', {})
            scene = scenes.get(scene_id, {})
            shots = scene.get('shots', {})
            shot = shots.get(shot_id)

            if shot:
                assets = shot.get('assets', {}).keys()
            else:
                assets = show.get('assets', {}).keys()

            for asset in assets:
                scopes.append({
                    'name': asset.replace('_', ' ').title(),
                    'id': asset
                })

        return map(
            partial(
                self.session.instantiate, 'harmony:/scope/{0}'.format(scope)
            ),
            scopes
        )


def main(arguments=None):
    '''Interactive test of dynamic UI building from schema.'''
    if arguments is None:
        arguments = sys.argv

    application = QtGui.QApplication(arguments)

    session = harmony.session.Session()
    dialog = Demo(session)
    dialog.resize(600, 800)
    dialog.show()

    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main())

