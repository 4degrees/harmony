# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import urlparse
from abc import ABCMeta, abstractmethod

import harmony.schema


class Processor(object):
    '''Process schemas.'''

    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, schemas):
        '''Process *schemas*
        :py:class:`collection <harmony.schema.collection.Collection>`.

        .. note::

            *schemas* are modified in place.

        '''


class MixinProcessor(Processor):
    '''Expand mixin references in schemas.'''

    def process(self, schemas):
        '''Process *schemas*
        :py:class:`collection <harmony.schema.collection.Collection>`.

        Expand 'mixin' references in schemas, essentially flattening the
        schemas.

        .. note::

            *schemas* will be modified in place.

        '''
        # Process schemas
        for schema in schemas:
            self._process(schema, schemas)

    def _process(self, fragment, schemas):
        '''Process a schema *fragment* against *schemas* collection.'''
        # Recurse into relevant fragments.
        # TODO: Can this reuse jsonschema code at all?
        properties = fragment.get('properties', {})
        for value in properties.values():
            if isinstance(value, dict):
                self._process(value, schemas)

        items = fragment.get('items', [])
        for item in items:
            if isinstance(item, dict):
                self._process(item, schemas)

        # Process mixin directives
        mixins = fragment.pop('$mixin', None)
        if not mixins:
            return

        if isinstance(mixins, dict):
            mixins = [mixins]

        for entry in mixins:
            reference = entry.get('$ref')
            if not reference:
                raise KeyError('No $ref defined for mixin.')

            parts = urlparse.urlsplit(reference)
            if parts.scheme != 'harmony':
                # TODO: Support resolving other schemes. Perhaps reuse
                # jsonschema RefResolver.
                continue

            # Lookup referenced schema for mixin.
            mixin = schemas.get(reference)

            # Ensure mixin has also been processed.
            self._process(mixin, schemas)

            # Merge mixin into the referring fragment.
            harmony.schema.merge(fragment, mixin)

