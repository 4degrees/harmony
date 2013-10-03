# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys
import time
from functools import partial

from PySide import QtGui

import harmony.session
import harmony.ui.widget.factory
import harmony.ui.error_tree
import harmony.ui.publisher


class Publisher(harmony.ui.publisher.Publisher):
    '''Customised publisher.'''

    def _publish(self, instance):
        '''Perform publish.'''
        for index in range(5):
            time.sleep(1)

        return instance


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
    factory = Factory(session)
    dialog = Publisher(session, factory)
    dialog.resize(600, 800)
    dialog.show()

    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main())

