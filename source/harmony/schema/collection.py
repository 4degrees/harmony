# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from ..error import SchemaConflictError


class Collection(object):
    '''Store registered schemas.'''

    def __init__(self, schemas=None):
        '''Initialise collection with *schemas*.'''
        self._schemas = {}
        if schemas is not None:
            for schema in schemas:
                self.add(schema)

    def add(self, schema):
        '''Add *schema*.

        Raise SchemaConflictError if a schema with the same id already exists.

        '''
        schema_id = schema['id']

        try:
            self.get(schema_id)
        except KeyError:
            self._schemas[schema_id] = schema
        else:
            raise SchemaConflictError('A schema is already registered with '
                                      'id {0}'.format(schema_id))

    def remove(self, schema_id):
        '''Remove a schema with *schema_id*.'''
        try:
            self._schemas.pop(schema_id)
        except KeyError:
            raise KeyError('No schema found with id {0}'.format(schema_id))

    def clear(self):
        '''Remove all registered schemas.'''
        self._schemas.clear()

    def get(self, schema_id):
        '''Return schema registered with *schema_id*.

        Raise KeyError if no schema with *schema_id* registered.

        '''
        try:
            schema = self._schemas[schema_id]
        except KeyError:
            raise KeyError('No schema found with id {0}'.format(schema_id))
        else:
            return schema

    def items(self):
        '''Yield (id, schema) pairs.'''
        for schema in self:
            yield (schema['id'], schema)

    def __iter__(self):
        '''Iterate over registered schemas.'''
        for schema_id in self._schemas:
            yield self.get(schema_id)
