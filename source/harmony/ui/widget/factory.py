# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from functools import partial

from PySide import QtGui

from .container import Container
from .string import String
from .text import Text
from .datetime import DateTime
from .enum import Enum
from .integer import Integer
from .number import Number
from .boolean import Boolean
from .array import Array

from ..model.templated_dictionary_list import TemplatedDictionaryList


class Factory(object):
    '''Manage constructing widgets for schemas.'''

    def __init__(self, session):
        '''Initialise factory with *session*.'''
        super(Factory, self).__init__()
        self.session = session

    def __call__(self, schema, options=None):
        '''Return an appropriate widget for *schema*.'''
        schema_type = schema.get('type')
        schema_title = schema.get('title')
        schema_description = schema.get('description')
        schema_id = schema.get('id', '')

        # IDs
        if schema_id == 'harmony:/user':
            user_model = TemplatedDictionaryList(
                '{firstname} {lastname} ({email})',
                self._query_users()
            )

            return Enum(
                user_model,
                title=schema_title,
                description=schema_description
            )

        # Primitives
        if schema_type == 'object':
            # Construct child for each property.
            children = []
            properties = schema.get('properties', {})

            def order(item):
                '''Order item by 'order' key else by name.'''
                return item[1].get('order', item[0])

            required = schema.get('required')
            hide = ['harmony_type']
            disable = []

            for name, subschema in sorted(properties.items(), key=order):
                child_widget = self(subschema, options=options)

                if name in required:
                    child_widget.setRequired(True)

                if name in hide:
                    child_widget.setHidden(True)

                if name in disable:
                    child_widget.setDisabled(True)

                children.append({'name': name, 'widget': child_widget})

            # Determine columns in layout.
            columns = 1
            if (schema_id in ('harmony:/user', 'harmony:/resolution')
                or schema_id.startswith('harmony:/scope/')):
                columns = 2

            return Container(
                title=schema_title,
                description=schema_description,
                children=children,
                columns=columns
            )

        if schema_type == 'array':
            items = schema.get('items', [])
            if isinstance(items, dict):
                additional_item = items
                items = []
            else:
                additional_item = schema.get('additionalItems', None)

            types = []
            for subschema in items:
                types.append({
                    'constructor': partial(self, subschema, options=options),
                    'value': self.session.instantiate(subschema)
                })

            additional_type = None
            if additional_item is not None:
                additional_type = {
                    'constructor': partial(self, additional_item,
                                           options=options),
                    'value': self.session.instantiate(additional_item)
                }

            return Array(
                title=schema_title,
                description=schema_description,
                types=types,
                additionalType=additional_type
            )

        if schema_type == 'string':
            if 'enum' in schema:
                return Enum(
                   title=schema_title,
                   description=schema_description,
                   model=QtGui.QStringListModel(schema['enum'])
                )
            elif schema.get('format', '') == 'text':
                return Text(
                    title=schema_title,
                    description=schema_description
                )
            elif schema.get('format', '') == 'date-time':
                return DateTime(
                    title=schema_title,
                    description=schema_description
                )
            else:
                return String(
                    title=schema_title,
                    description=schema_description
                )

        if schema_type == 'integer':
            return Integer(
                title=schema_title,
                description=schema_description,
                minimum=schema.get('minimum'),
                maximum=schema.get('maximum')
            )

        if schema_type == 'number':
            return Number(
                title=schema_title,
                description=schema_description,
                minimum=schema.get('minimum'),
                maximum=schema.get('maximum')
            )

        if schema_type == 'boolean':
            return Boolean(
                title=schema_title,
                description=schema_description
            )

        raise ValueError('No widget able to represent schema: {0}'
                         .format(schema))

    def _query_users(self):
        '''Return a list of valid users.'''
        users = []
        for user in [
            {'firstname': 'Martin', 'lastname': 'Pengelly-Phillips',
             'email': 'martin@4degrees.ltd.uk', 'username': 'martin'},
            {'firstname': 'Joe', 'lastname': 'Blogs',
             'email': 'joe@example.com', 'username': 'joe'}
        ]:
            user = self.session.instantiate('harmony:/user', user)
            users.append(user)

        return users

