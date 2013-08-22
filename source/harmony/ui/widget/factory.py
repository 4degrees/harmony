# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from .container import Container
from .string import String
from .text import Text
from .enum import Enum
from .integer import Integer
from .number import Number
from .boolean import Boolean


class Factory(object):
    '''Manage constructing widgets for schemas.'''

    def __call__(self, schema, options=None):
        '''Return an appropriate widget for *schema*.'''
        schema_type = schema.get('type')
        schema_title = schema.get('title')
        schema_description = schema.get('description')

        if schema_type == 'object':
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

            return Container(
                title=schema_title,
                description=schema_description,
                children=children
            )

        if schema_type == 'string':
            if 'enum' in schema:
                return Enum(
                   title=schema_title,
                   description=schema_description,
                   items=schema['enum']
                )
            elif schema.get('format', '') == 'text':
                return Text(
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

